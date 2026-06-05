"""
Recommendation engine for crop treatment suggestions.

Provides intelligent recommendations for crop treatment based on classification
results with confidence-based filtering to reduce false positives.
"""

import logging

logger = logging.getLogger(__name__)

# Confidence threshold below which recommendations should not be made
CONFIDENCE_THRESHOLD = 0.85


def generate_recommendations(classification_result, classification_confidence,
                           disease_info=None):
    """
    Generate treatment recommendations based on crop classification.

    Implements confidence threshold gating to prevent false positive
    recommendations for healthy crops.

    Args:
        classification_result (str): Classification output ('healthy', 'disease_name', etc.)
        classification_confidence (float): Confidence score of the classification (0-1)
        disease_info (dict, optional): Additional disease information if applicable

    Returns:
        dict: Recommendation with action, reasoning, and confidence score
    """

    # Confidence threshold gating - prevent low-confidence recommendations
    if classification_confidence < CONFIDENCE_THRESHOLD:
        logger.warning(
            f"Classification confidence {classification_confidence} below threshold "
            f"{CONFIDENCE_THRESHOLD}. Returning no-treatment recommendation."
        )
        return {
            'action': 'no_treatment',
            'reason': 'insufficient_confidence',
            'confidence_score': classification_confidence,
            'message': 'Confidence too low for accurate treatment recommendation. '
                      'Please consult with an agricultural expert.',
            'recommendation': 'No treatment recommended at this time',
            'explanation': 'The model was not confident enough in its classification '
                          'to make a safe treatment recommendation.'
        }

    # Healthy crop classification
    if classification_result.lower() == 'healthy':
        logger.info(
            f"Healthy crop classification with confidence {classification_confidence}"
        )
        return {
            'action': 'maintain_current_practices',
            'recommendation': 'No treatment needed',
            'confidence_score': classification_confidence,
            'message': 'Your crop appears healthy',
            'explanation': 'The crop shows no signs of disease or nutritional deficiency. '
                          'Continue with regular maintenance practices.',
            'suggested_practices': [
                'Maintain regular watering schedule',
                'Monitor for pest activity',
                'Continue current fertilization schedule'
            ]
        }

    # Disease classification with sufficient confidence
    if disease_info is None:
        disease_info = {}

    logger.info(
        f"Disease recommendation for {classification_result} "
        f"with confidence {classification_confidence}"
    )

    return {
        'action': 'apply_treatment',
        'disease': classification_result,
        'confidence_score': classification_confidence,
        'message': f'Treatment recommended for {classification_result}',
        'recommendation': _get_treatment_for_disease(classification_result, disease_info),
        'explanation': f'The crop has been classified as having {classification_result} '
                      f'with {classification_confidence*100:.1f}% confidence.',
        'treatment_plan': _get_treatment_plan(classification_result, disease_info)
    }


def _get_treatment_for_disease(disease_name, disease_info=None):
    """
    Get recommended treatment for identified disease.

    Args:
        disease_name (str): Name of the disease
        disease_info (dict, optional): Additional disease context

    Returns:
        str: Treatment recommendation
    """
    # Standard treatment mappings
    treatments = {
        'leaf_spot': 'Apply fungicide (e.g., Chlorothalonil or Mancozeb)',
        'powdery_mildew': 'Apply sulfur-based fungicide or wettable powder',
        'rust': 'Apply rust-specific fungicide and improve air circulation',
        'blight': 'Apply copper-based fungicide and remove infected parts',
        'leaf_curl': 'Apply insecticide for pest control and fungicide for secondary infections',
        'root_rot': 'Improve drainage, reduce watering frequency, apply root treatment fungicide',
        'nutrient_deficiency_nitrogen': 'Apply nitrogen-rich fertilizer (urea or ammonium nitrate)',
        'nutrient_deficiency_phosphorus': 'Apply phosphorus fertilizer (superphosphate)',
        'nutrient_deficiency_potassium': 'Apply potassium fertilizer (muriate of potash)',
    }

    return treatments.get(disease_name.lower(),
                        f'Consult with agricultural expert for {disease_name} treatment')


def _get_treatment_plan(disease_name, disease_info=None):
    """
    Get detailed treatment plan for identified disease.

    Args:
        disease_name (str): Name of the disease
        disease_info (dict, optional): Additional disease context

    Returns:
        list: Step-by-step treatment plan
    """
    plan = {
        'immediate_action': 'Begin treatment within 24-48 hours',
        'application_schedule': 'Apply every 7-10 days for 3-4 weeks or as product label directs',
        'monitoring': 'Monitor crop daily for improvement',
        'follow_up': 'After 2 weeks, assess effectiveness and adjust if needed',
        'prevention': 'After treatment, maintain good sanitation and crop rotation'
    }

    return plan


def validate_recommendation(recommendation):
    """
    Validate recommendation format and required fields.

    Args:
        recommendation (dict): Recommendation to validate

    Returns:
        bool: True if recommendation is valid

    Raises:
        ValueError: If recommendation is missing required fields
    """
    required_fields = ['action', 'confidence_score', 'message']

    for field in required_fields:
        if field not in recommendation:
            raise ValueError(f"Recommendation missing required field: {field}")

    if not 0 <= recommendation.get('confidence_score', 0) <= 1:
        raise ValueError("Confidence score must be between 0 and 1")

    return True
