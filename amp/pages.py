"""
Affect Misattribution Procedure (AMP) experiment -- pages.

Display trials per round, handle submitted trial responses.

November 2019
Markus Konrad <markus.konrad@wzb.eu>
"""

import os
import random
from itertools import product

from ._builtin import Page
from .models import Constants, Trial


class IntroPage(Page):
    def is_displayed(self):
        return self.round_number == 1


class AMPPage(Page):
    """
    AMP base class to display AMP trials and handle submitted trial responses.
    """

    def vars_for_template(self):
        # get trials generated for this player ordered by trial number
        trials = Trial.objects.filter(player=self.player).order_by('trial')

        return {
            'trials': trials,
            'is_practice': False
        }

    def before_next_page(self):
        """
        Handle submitted trial responses.
        """

        # trial IDs, response keys and response times are submitted as aligned, comma separated values
        # split them
        trial_ids = self.form.data['trial_ids'].split(',')
        responses = self.form.data['responses'].split(',')
        response_times = self.form.data['response_times'].split(',')

        if not trial_ids:
            raise ValueError('no input data for `trial_ids`')

        if not responses:
            raise ValueError('no input data for `responses`')

        if not response_times:
            raise ValueError('no input data for `response_times`')

        if len(trial_ids) != len(responses) or len(responses) != len(response_times):
            raise ValueError('input data for `trial_ids` (%d elements), `responses` (%d elements) and '
                             '`response_times` (%d elements) are of different length'
                             % (len(trial_ids), len(responses), len(response_times)))

        print('number of trials submitted from player %d: %d' % (self.player.pk, len(trial_ids)))

        # iterate through the aligned responses
        for trial_id, resp_key, resp_time_ms in zip(trial_ids, responses, response_times):
            # convert strings to integers
            trial_id = int(trial_id)
            resp_time_ms = int(resp_time_ms)

            # fetch the Trial object
            trial = Trial.objects.get(pk=trial_id, player=self.player)

            # store the responses
            trial.response_key = resp_key
            trial.response_time_ms = resp_time_ms

            print('> saving trial %d (trial ID %d): key %s, time %d'
                  % (trial.trial, trial.pk, trial.response_key, trial.response_time_ms))

            trial.save()


class AMPPracticePage(AMPPage):
    template_name = 'amp/AMPPage.html'

    def vars_for_template(self):
        def files_in_dir(dir):
            return [f for f in os.listdir(dir) if not f.startswith('.') and os.path.isfile(os.path.join(dir, f))]

        prime_images = files_in_dir(os.path.join('_static', 'amp', 'primes_practice'))
        target_images = files_in_dir(os.path.join('_static', 'amp', 'targets_practice'))

        # randomized cartesian product of primes and targets
        primes_targets = list(product(prime_images, target_images))
        random.shuffle(primes_targets)

        trials = [{'pk': 0, 'prime_class': '', 'prime': prime, 'target_class': '', 'target': target}
                  for prime, target in primes_targets]

        return {
            'trials': trials,
            'is_practice': True,
        }

    def before_next_page(self):
        pass   # practice page - don't record anything

    def is_displayed(self):
        return self.round_number == 1


class AMPFinished(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds


page_sequence = [
    IntroPage,
    AMPPracticePage,
    AMPPage,
    AMPFinished,
]
