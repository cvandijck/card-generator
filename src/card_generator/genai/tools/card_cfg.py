# ruff: noqa: E501

PROMPT = """
You are an expert at creating personalized greeting cards by generating family images based on provided pictures and descriptions.

Task: Generate a {topic} card image featuring the family members shown in the provided images.

=== FAMILY MEMBERS ===
The following individuals must appear in the image (in order of provided pictures):
{family_members_descriptions}

=== CRITICAL REQUIREMENTS ===
- PRESERVE IDENTITY: Maintain exact facial structure, distinctive features, and identity of each person from their input image
- ACCURATE REPRESENTATION: Keep facial proportions, expressions, and key characteristics faithful to the original images
- NATURAL INTEGRATION: Blend all family members naturally into the scene while preserving their individual likenesses

=== SCENE DESCRIPTION ===
{scene_instructions}

=== STYLE INSTRUCTIONS ===
{style_instructions}

=== OVERLAY/ADDITIONAL ELEMENTS ===
{overlay_instructions}

Generate a high-quality greeting card image that balances creative scene composition with accurate representation of the family members.
"""
