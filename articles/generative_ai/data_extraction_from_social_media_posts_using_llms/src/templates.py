PROFILES_REPORT_TEMPLATE = (
    "You're a Restaurnat specialist. Analyze social media posts from various restaurant pages and create a concise report extracting the following information:\n"
    "1. Giveaways\n"
    "2. Events (including dates)\n"
    "3. Deals and discounts (e.g., price reductions, 1+1 offers)\n"
    "4. New menu items\n"
    "For each item, include:\n"
    "- Restaurant page name"
    "- Post link"
    "- Restaurant location (city)\n"
    "Only include information from the provided posts that fits these categories. Avoid descriptive posts about dishes unless they mention specific offers or discounts.\n"
    "Posts to analyze: {input_var}"

)

PROFILES_TEMPLATE_REFINE = (
    "You're a restaurant specialist who has generated a report on various restaurant social media posts.\n"
    "Previous report: {raport}\n"
    "This report needs to be more concise and follow a predefined structure:\n"
    "1. Analyze your previous report.\n"
    "2. Adapt the report to the following structure: {format_instructions}\n"
    "If there's no relevant information for a key, leave it as an empty list\n."
    "Your response should only contain the specified structure, without ```json ``` tags."
)
