"""
Affect Misattribution Procedure (AMP) experiment -- tests.

August 2019
Markus Konrad <markus.konrad@wzb.eu>
"""


import random

from . import pages
from ._builtin import Bot
from .models import Constants, Trial, get_amp_images


avail_response_keys = list(Constants.capture_keycodes.keys())
avail_prime_images = get_amp_images('primes')
avail_target_images = get_amp_images('targets')


class PlayerBot(Bot):
    def play_round(self):
        if self.round_number == 1:
            yield pages.IntroPage
            yield pages.AMPPracticePage

        # check existing Trial objects in DB
        trials_pre = Trial.objects.filter(player=self.player).order_by('trial')
        n_trials_pre = len(trials_pre)
        assert n_trials_pre > 0

        for i, t in enumerate(trials_pre):
            assert t.trial == i+1
            assert t.player == self.player

            # must be set:
            assert t.prime_class in avail_prime_images.keys()
            assert t.prime in avail_prime_images[t.prime_class]
            assert t.target_class in avail_target_images.keys()
            assert t.target in avail_target_images[t.target_class]

            # must be empty before trial is run:
            assert t.response_key is None
            assert t.response_time_ms is None

        # prepare submit with random inputs for each trial
        trial_ids = [t.pk for t in trials_pre]
        response_keys = [random.choice(avail_response_keys) for _ in range(n_trials_pre)]
        response_times = [random.randint(100, 1100) for _ in range(n_trials_pre)]

        # submit trials
        yield (pages.AMPPage, {
            'trial_ids': ','.join(map(str, trial_ids)),
            'responses': ','.join(response_keys),
            'response_times': ','.join(map(str, response_times)),
        })

        # check stored Trial objects after submission
        trials_post = Trial.objects.filter(player=self.player).order_by('trial')
        n_trials_post = len(trials_post)
        assert n_trials_post == n_trials_pre

        for i, (t_pre, t_post) in enumerate(zip(trials_pre, trials_post)):
            assert t_pre.pk == t_post.pk == trial_ids[i]
            assert t_pre.trial == t_post.trial == i+1
            assert t_post.player == self.player

            # must be unchanged
            assert t_pre.prime == t_post.prime
            assert t_pre.prime_class == t_post.prime_class
            assert t_pre.target == t_post.target
            assert t_pre.target_class == t_post.target_class

            # must be set according to submitted values
            assert t_post.response_key == response_keys[i]
            assert t_post.response_time_ms == response_times[i]

        if self.round_number == Constants.num_rounds:
            yield pages.AMPFinished
