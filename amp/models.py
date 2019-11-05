"""
Affect Misattribution Procedure (AMP) experiment -- models.

Dynamic data points for AMP trials are collected in custom data model "Trial". See Konrad 2018 [1] for an article
on collection dynamic data with oTree using the package otreeutils [2].

[1] https://doi.org/10.1016/j.jbef.2018.10.006
[2] https://github.com/WZBSocialScienceCenter/otreeutils

November 2019
Markus Konrad <markus.konrad@wzb.eu>
"""

import os
import random

from otree.api import (
    models, BaseConstants, BaseSubsession, BaseGroup, BasePlayer
)

# required for custom data models:
from otree.db.models import Model, ForeignKey


author = 'Markus Konrad <markus.konrad@wzb.eu>'

doc = """
Affect Misattribution Procedure (AMP) experiment
"""


def get_amp_images(imgtype):
    """
    Load all available images for a certain image type `imgtype` (either "primes" or "targets"). Will return a dict
    with classes as keys and the corresponding image files as list inside, e.g. for the image type "targets":
    {
        'neg': ['t_neg01.jpg', ... ],
        'pos': ['t_pos01.jpg', ... ],
    }
    The file names will be loaded from the directory `_static/amp/<image type>/<classes>/`.
    """
    basedir = os.path.join('_static', 'amp', imgtype)

    classes = {}
    for f in os.listdir(basedir):
        path = os.path.join(basedir, f)
        if not f.startswith('.') and os.path.isdir(path):  # class folder
            classes[f] = []

            for f_class in os.listdir(path):               # file inside class folder
                imgpath = os.path.join(path, f_class)
                if not f_class.startswith('.') and os.path.isfile(imgpath):
                    classes[f].append(f_class)

    return classes


def sample_targets_and_primes(targets, primes, n_rounds,
                              already_sampled_targets=None, already_sampled_primes=None):
    """
    Sample targets `targets` and primes `primes` for `n_rounds` number of rounds. Omit already sampled targets
    or primes which can be passed as sets `already_sampled_targets` and `already_sampled_primes`.
    `targets` and `primes` must be dicts with class -> [files] mapping (as delivered from `get_amp_images`.

    Will return a sample of size "num. of target classes * number of targets per class // `n_rounds`" as list of
    4-tuples with:
    - target class
    - target file
    - prime class
    - prime file

    This function makes sure that you present N targets in random order split into R rounds, where each prime of each
    prime class is matched with a random target *per target class* by calling it as such:

    ```
    # round 1:
    sample_round_1 = sample_targets_and_primes(targets, primes, Constants.num_rounds)
    # round 2:
    sample_round_2 = sample_targets_and_primes(targets, primes, Constants.num_rounds,
                                               already_sampled_targets=<targets from sample_round_1>)
    ...
    ```
    """
    # set defaults
    if not already_sampled_targets:
        already_sampled_targets = set()
    if not already_sampled_primes:
        already_sampled_primes = set()

    # make sure we have sets
    if not isinstance(already_sampled_targets, set):
        raise ValueError('`already_sampled_targets` must be a set.')

    if not isinstance(already_sampled_primes, set):
        raise ValueError('`already_sampled_primes` must be a set.')

    # get number of classes
    n_prime_classes = len(primes)
    n_target_classes = len(targets)

    if not n_prime_classes:
        raise ValueError('No target images found.')

    if not n_target_classes:
        raise ValueError('No prime images found.')

    # create a list of primes with 2-tuples: (class, file)
    # order of primes is random inside prime class
    primes_list = []
    for primes_classname, class_primes in primes.items():
        class_primes = list(set(class_primes) - already_sampled_primes)  # omit already sampled primes
        # random order of primes inside class
        random.shuffle(class_primes)
        primes_list.extend(zip([primes_classname] * len(class_primes), class_primes))
    n_primes = len(primes_list)

    targets_round = []   # holds the output list with 4-tuples
    # construct a sample of targets per target class
    for target_classname, class_targets in targets.items():
        n_targets = len(class_targets)

        if n_targets % n_rounds != 0:
            raise ValueError('Number of targets in class (%d in "%s") must be a multiple of'
                             ' number of rounds (%d)'
                             % (n_targets, target_classname, n_rounds))

        # omit already sampled targets
        class_targets = set(class_targets) - already_sampled_targets

        # get a sample of class targets as random sample without replacement of size "number of targets divided
        # by number of rounds" so that you can split targets into several rounds
        targets_sample = random.sample(class_targets, n_targets // n_rounds)
        n_targets_sample = len(targets_sample)

        if n_targets_sample % n_primes != 0:
            raise ValueError('Number of sampled targets in class (%d in "%s") must be a multiple of'
                             ' number of primes (%d)'
                             % (n_targets_sample, target_classname, n_primes))

        # primes sample is the primes list repeated so that it matches the length of targets in this target class
        # this makes sure that for each target class all primes will be shown
        primes_sample = primes_list * (n_targets_sample // n_primes)
        primes_sample_classes, primes_sample_prime = list(zip(*primes_sample))

        assert len(primes_sample) == n_targets_sample

        # add targets-primes combinations for this round
        targets_round.extend(zip([target_classname] * n_targets_sample, targets_sample,
                                 primes_sample_classes, primes_sample_prime))

    # random order of targets-primes combinations
    random.shuffle(targets_round)

    return targets_round


class Constants(BaseConstants):
    name_in_url = 'amp'
    players_per_group = None
    num_rounds = 2                  # AMP rounds aka "blocks"
    #debug_n_trials_per_round = 10   # for debugging, show only this number of trials per round (set to None to disable)
    debug_n_trials_per_round = None
    allow_input_during_target_presentation = False    # allow pressing keys during target presentation. if set to
                                                      # False, keys are only captured once target presentation is over
    hurry_up_message_after_ms = 3000   # set to 0 or less to disable

    # experiment display setup:
    # there are 4 stages:
    # 1. display prime
    # 2. display blank screen
    # 3. display target
    # 4. display noise mask
    # duration can be set here in milliseconds
    init_ms = 0       # time before prime display
    prime_ms = 75     # duration of prime display
    blank_ms = 125    # duration of blank screen display
    target_ms = 100   # duration of target display

    # key codes and their labels that will be captured as inputs
    # JavaScript key code as from https://keycode.info/
                        # code:  key to display, label to display
    capture_keycodes = {'KeyQ': ('Q', 'Unappealing'),
                        'KeyP': ('P', 'Appealing')}


class Subsession(BaseSubsession):
    def creating_session(self):
        """
        Prepare trials for each round. Generates Trial objects.
        """

        # load primes and targets
        primes = get_amp_images('primes')
        targets = get_amp_images('targets')

        # iterate through all players in all rounds
        for p in self.get_players():
            # obtain targets that were already used for this participant in previous rounds
            prev_targets = set()
            for prev_p in p.in_previous_rounds():
                for trial in Trial.objects.filter(player=prev_p):
                    prev_targets.add(trial.target)

            # generate sample of targets and primes to display
            sample = sample_targets_and_primes(targets, primes, Constants.num_rounds,
                                               already_sampled_targets=prev_targets)

            if Constants.debug_n_trials_per_round:
                sample = sample[:Constants.debug_n_trials_per_round]

            # generate Trial objects
            trials = []
            print('participant %d, player %d, round %d: creating %d trials'
                  % (p.participant.pk, p.pk, self.round_number, len(sample)))
            for i_trial, (target_class, target, prime_class, prime) in enumerate(sample):
                print('> trial %d with target %s (%s), prime %s (%s)'
                      % (i_trial + 1, target, target_class, prime, prime_class))
                trials.append(Trial(trial=i_trial + 1,
                                    target_class=target_class, target=target,
                                    prime_class=prime_class, prime=prime,
                                    player=p))

            # store them to DB
            Trial.objects.bulk_create(trials)


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


class Trial(Model):
    """
    Trial model holds all information for a single trial made by a player.
    This is a "custom data model" in a 1:n relationship between Player and Trial.
    It uses an otreeutils "CustomModelConf" for monitoring and exporting the collected data from this model.
    """
    trial = models.IntegerField()             # trial number in that round for that participant
    prime = models.StringField()              # prime image to be displayed
    prime_class = models.StringField()        # class of prime (corresponds to folder name in _static/amp/primes)
    target = models.StringField()             # target image to be displayed
    target_class = models.StringField()       # class of target (corresponds to folder name in _static/amp/targets)
    response_key = models.StringField()       # response: key that was pressed by participant
    response_time_ms = models.IntegerField()  # time it took until key was pressed since either the target is displayed
                                              # or *after* the target was displayed, depending on
                                              # Constants.allow_input_during_target_presentation

    player = ForeignKey(Player)               # make a 1:n relationship between Player and Trial

    class CustomModelConf:
        """
        Configuration for otreeutils admin extensions.
        """
        data_view = {  # define this attribute if you want to include this model in the live data view
            'exclude_fields': ['player'],
            'link_with': 'player'
        }
        export_data = {  # define this attribute if you want to include this model in the data export
            'exclude_fields': ['player_id'],
            'link_with': 'player'
        }
