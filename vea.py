'''
TO-DO
1. Write generate_sample
2. Get linear model working
3. Implement feature extraction
4. Implement algos #4, 5
5. Visualization?
'''


from profile import Profile
from math import log10
from math import floor
import operator
import copy

# This is the Visualizable Evidence-Driven Approach (VEA) method

# An event contains a list of evidence units
class Event:
    def __init__(self, modality, num_authors):
        self.modality = modality
        self.confidence = None
        self.scores = [None] * num_authors
        self.evidence_units = []

    def add_eu(self, evidence_unit):
        self.evidence_units.append(evidence_unit)

# An evidence unit is ONE feature (one word, one character)
class EvidenceUnit:
    def __init__(self, feature, modality, num_authors):
        self.modality = modality
        self.feature = feature
        self.num_authors = num_authors
        self.scores = [None] * num_authors
        self.idf = 0
    
    def calculate_idf(self, candidates):
        authors_ever_used = 0
        for candidate in candidates:
            if (candidate.find_feature(self.feature)):
                authors_ever_used += 1

        constant = 0.1
        num_authors = candidates.length

        self.idf = log10(num_authors / (constant + authors_ever_used))


# Example: If modality is "word", content could be "it is" and length "2"
class Feature:
    def __init__(self, content, length, modality, frequency):
        self.content = content
        self.length = length
        self.modality = modality
        self.frequency = frequency

class VEAProfile(Profile):
    def __init__(self, profile):
        self.single_text = profile.single_text
        self.texts = profile.texts

        self.word_features = None
        self.character_features = None
        self.pos_features = None

    # Find matching feature
    def find_feature(self, feature):
        features_of_modality = []
        if feature.modality == "word":
            features_of_modality = self.word_features
        elif feature.modality == "character":
            features_of_modality = self.character_features
        elif feature.modality == "pos":
            features_of_modality = self.pos_features

        for self_feature in features_of_modality:
            if self_feature.content == feature.content:
                return self_feature
        
        return None

    def find_max_feature_frequency(modality):
        features_of_modality = []
        if modality == "word":
            features_of_modality = self.word_features
        elif modality == "character":
            features_of_modality = self.character_features
        elif modality == "pos":
            features_of_modality = self.pos_features

        max_frequency = 0
        for feature in features_of_modality:
            if feature.frequency > max_frequency:
                max_frequency = feature.frequency

        return max_frequency

    # Used by algorithm #3
    # We're doing a 10-fold cross-validation test
    # If fold_number = 0, return first 10% of samples
    # as testing, last 90% of samples as training
    def generate_fold_samples(fold_number):
        # If number of texts is divisible by 10, things are easy
        # We don't need to break up any samples
        if len(self.texts) % 10 == 0:
            test_group_len = len(self.texts) / 10
            test_group_min = fold_number * test_group_len
            test_group_max = fold_number * test_group_len + test_group_len

            test_group = self.texts[test_group_min:test_group_max]
            training_group = self.texts[0:test_group_min] + self.texts[test_group_max:]

        # If number of texts is NOT divisible by 10, add all the samples together
        # And divide them into 10 slices
        else:
            # First, find length of one slice
            num_chars = len(self.single_text)
            if num_chars % 10 == 0:
                slice_len = num_chars / 10
            else:
                # In this case, the last slice will be slightly longer than the other slices
                slice_len = int(floor(num_chars / 10.))

            # Now generate indices of groups
            test_group_min = fold_number * slice_len
            test_group_max = fold_number * slice_len + slice_len
            
            test_group = self.single_text[test_group_min:test_group_max]
            training_group = self.single_text[0:test_group_min] + self.single_text[test_group_max:]
            
        return test_group, training_group


def extract_word_features(anon_profile):
    pass

def extract_character_features(anon_profile):
    pass

def extract_pos_features(anon_profile):
    pass

def construct_event(features, modality, num_authors):
    event = Event(modality, num_authors)
    for feature in features:
        eu = EvidenceUnit(feature, modality, num_authors)
        event.add_eu(eu)

    return event

# ALGORITHM 1
def create_event(candidate_profiles, anon_profile, modality):
    num_authors = len(candidate_profiles)
    if modality == "word":
        word_features = extract_word_features(anon_profile)
        word_event = construct_event(word_features, "word", num_authors)
        return word_event

    if modality == "character":
        character_features = extract_character_features(anon_profile)
        character_event = construct_event(character_features, "character", num_authors)
        return character_event

    if modality == "pos":
        pos_features = extract_pos_features(anon_profile)
        pos_event = construct_event(pos_features, "pos", num_authors)
        return pos_event


def create_events(candidate_profiles, anon_profile):
    num_authors = len(candidate_profiles)
    events = []
    modalities = ("word", "character", "pos")
    for modality in modalities:
        new_event = create_event(candidate_profiles, anon_profile, modality)
        events.append(new_event)
    
    return events


def tf(feature, candidate):
    modality = feature.modality

    candidate_feature = candidate.find_feature(feature)
    if (candidate_feature):
        frequency = candidate_feature.frequency
    else:
        frequency = 0

    max_feature_frequency = candidate.find_max_feature_frequency(modality)
    if max_feature_frequency == 0:
        return 0

    return frequency / max_feature_frequency

# Find word, character, POS features in candidates
def extract_candidate_features(candidate_profiles):
    candidates = []
    for candidate_profile in candidate_profiles:
        candidate = VEAProfile(candidate_profile)

        candidate.word_features = extract_word_features(candidate)
        candidate.character_features = extract_character_features(candidate)
        candidate.pos_features = extract_pos_features(candidate)

        candidates.append(candidate)

    for index, event in enumerate(events):
        for eu_index, eu in enumerate(event.evidence_units):
            eu.calculate_idf(candidates)
            events[index].evidence_units[eu_index] = eu

    return candidates

# ALGORITHM 2
def score_event(event, anon_profile, candidates):
    # Lines 2-5
    # Score each feature based on TF for anon_profile
    anon_scores = []
    for eu in event.evidence_units:
        feature_score = tf(eu.feature, anon_profile)
        anon_scores.append(feature_score)

    # Lines 6-13
    # Score each feature based on TF-IDF for candidates
    for index, candidate in enumerate(candidates):
        candidate_scores = []
        for eu_index, eu in enumerate(event.evidence_units):
            score = tf(eu.feature, candidate) * eu.idf
            eu.scores[index] = score * anon_scores[eu_scores]
            candidate_scores.append(score)

        dot_product = sum(map(operator.mul, anon_scores, candidate_scores))
        event.scores[index] = dot_product


def score_events(events, anon_profile, candidates):
    for event in events:
        score_event(event, anon_profile, candidates)

# Needed for Algorithm 3
# Return testing group and training group (containing profiles)
# Given the fold #
def generate_fold_groups(fold_number, candidates):
    testing_group, training_group = [], []
    for candidate in candidates:
        testing_sample, training_sample = candidate.generate_fold_samples(fold_number)

        testing_profile = Profile(testing_sample)
        testing_group.append(testing_profile)

        training_profile = Profile(training_sample)
        training_group.append(training_profile)

    return testing_group, training_group

# ALGORITHM 3
'''
For each event...
    Divide each candidate's samples into 10 groups
    Collate these 10 groups of every author into 10 supergroups, each containing each writer
    For every supergroup...
        testing_group = supergroup
        training_group = all supergroups except this one
        For every author_sample in testing_group:
            anon_profile = author_sample
            candidate_profiles = samples from training_group
            run algos #1 and #2 on them
            keep track of whether predicted author is actual author
            collect sample
        collect samples
    build linear model from samples
    using samples of real event, predict confidence
'''
def author_is_correct(event, real_author_index):
    # Find predicted author
    predicted_author_index = -1
    for index, score in enumerate(event.scores):
        if predicted_author_index == -1 or score > event.scores[predicted_author_index]:
            predicted_author_index = index

    return predicted_author_index == real_author_index

def generate_sample(event, profile):
    pass

def estimate_confidence(events, anon_profile, candidates):
    samples = []
    for event in events:
        for fold_number in range(10):
            correct_guess = 0
            fold_samples = []
            testing_group, training_group = generate_fold_groups(fold_number, candidates)

            # lines 6-16
            for author_index, test_doc in enumerate(testing_group):
                candidates_temp = copy.copy(training_group)
                test_event = create_event(candidates_temp, test_doc, event.modality)
                candidates = extract_candidate_features(candidates_temp, test_event)
                score_event(test_event, test_doc, candidates)
                if author_is_correct(test_event, author_index):
                    correct_guess += 1

                sample = generate_sample(test_event, test_doc)
                fold_samples.append(sample)
            
            # lines 17-20
            precision = correct_guess / len(testing_group)
            for sample in fold_samples:
                sample.append(precision)

            # line 21
            samples += fold_samples

        model = build_model(samples)
        estimated_confidence = model.predict(generate_sample(event, anon_profile))
        return estimated_confidence
                

def analyze(anon_profile, candidate_profiles):
    events = create_events(candidate_profiles, anon_profile)
    candidates = extract_candidate_features(candidate_profiles, events)
    score_events(events, anon_profile, candidates)
    estimate_confidence(events, anon_profile, candidates)
