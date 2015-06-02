from profile import Profile
from math import log10
import operator

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
def create_events():
    num_authors = len(candidate_profiles)

    word_features = extract_word_features(anon_profile)
    word_event = construct_event(word_features, "word", num_authors)

    character_features = extract_character_features(anon_profile)
    character_event = construct_event(character_features, "character", num_authors)

    pos_features = extract_pos_features(anon_profile)
    pos_event = construct_event(pos_features, "pos", num_authors)

    return (word_features, character_features, pos_features)


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
def score_events(events, anon_profile, candidates):
    for event in events:
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
            scores[index] = dot_product

def analyze(anon_profile, candidate_profiles):
    events = create_events()
    candidates = extract_candidate_features(candidate_profiles, events)
    events = score_events(events, anon_profile, candidates)
