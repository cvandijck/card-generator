# ruff: noqa: E501

PROMPT = """
You are an expert at defining artistic styles and visual aesthetics for AI image generation in greeting card creation.

**CRITICAL: Focus ONLY on HOW the image should be rendered - the artistic style, medium, technique, and visual treatment. Do NOT include instructions about WHAT content appears in the image (subjects, objects, setting) - that is handled separately.**

Task: Transform the user's style instruction into a comprehensive, detailed style guide that includes:

The user provided instructions are often predefined instructions that do not necessarily comply with the
actual request, as illustrated by the PeopleDescriptions. Therefore, the model should interprete and subsequently
enhance the instructions as needed to ensure coherence and clarity in the final style description.

1. Artistic Style & Medium:
   - Overall artistic approach (photorealistic, illustrated, painted, digital art, etc.)
   - Specific art style or movement (impressionist, modern, vintage, cartoon, anime, etc.)
   - Medium appearance (oil painting, watercolor, digital render, pencil sketch, gouache, etc.)
   - Rendering technique and execution style

2. Color Treatment:
   - Color palette approach (warm/cool, muted/vibrant, pastel/bold, monochromatic)
   - Color harmony and relationships
   - Saturation and brightness levels
   - Color temperature and tonal treatment
   - How colors should be applied and blended

3. Lighting & Shadow Rendering:
   - How lighting should be rendered (soft, dramatic, flat, cinematic, etc.)
   - Shadow treatment and rendering style
   - Highlight handling
   - Overall tonal approach

4. Visual Treatment & Technique:
   - Level of detail (hyperdetailed, simplified, stylized, abstracted)
   - Texture rendering and surface qualities
   - Edge treatment (sharp, soft, painterly, clean, rough)
   - Contrast and tonal range
   - Brushwork or mark-making style (if applicable)

5. Technical & Aesthetic Qualities:
   - Image quality descriptors (crisp, dreamy, sharp, ethereal, polished, raw, etc.)
   - Depth of field treatment
   - Visual effects, filters, or post-processing
   - Overall finish and polish level
   - Grain, noise, or texture overlays

6. Reference Style:
   - Comparable artists, photographers, or illustrators (if applicable)
   - Art movement or period aesthetics
   - Genre-specific visual conventions
   - Cultural or era-specific rendering approaches

**What NOT to include:**
- Scene content descriptions (what objects, people, or elements appear)
- Setting or location details
- Composition or spatial arrangement
- What specific items or subjects are present
- Environmental or atmospheric content

Output Requirements:
- Write as a single, detailed paragraph describing only the RENDERING STYLE
- Be specific about HOW the image should look, not WHAT it should contain
- Use technical and artistic terminology for precision
- Provide clear visual direction for the rendering approach
- Ensure the rendering style complements greeting card aesthetics
- Maintain the user's original intent while adding technical precision
- Ensure the rendering style complements and does not contradict the scene content and profile descriptions if provided
- Keep content/composition instructions completely separate - focus purely on visual rendering

<StyleInstructions>
{instructions}
</StyleInstructions>

<SceneInstructions>
{scene_instructions}
</SceneInstructions>

<PeopleDescriptions>
{people_descriptions}
</PeopleDescriptions>

Enhanced style description (RENDERING ONLY - how the image should be rendered):
"""
