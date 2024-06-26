PROFILES_REPORT_TEMPLATE = (
    'You are a specialist in the HORECA field. \n'
    'Your task is to analyze multiple posts from different social media pages owned by various restaurants. \n'
    'Then you need to create a report where you present specific information extracted from the content of the posts. \n'
    'To accomplish this task, the following steps must be followed: \n'
    'Step 1: Analyze the content of the received posts: {input_var} \n'
    'Step 2: Extract information related to giveaways. Generally, the posts contain words like "giveaway". \n'
    'Step 3: Extract information related to events (in the case of events, the date when they are organized must also be extracted). \n'
    '   These can fall into the following categories: \n'
    '       - Parties \n'
    '       - Wine tastings \n'
    '       - New/seasonal menu launches \n'
    '       - Brunch & music \n'
    '       - Live music in the venue/band \n'
    'Step 4: Extract information related to deals, discounts, and offers. These may consist of: discounts, 1+1 type offers, etc. \n'
    'ATTENTION! Avoid descriptive posts about dishes where there is no mention of a specific offer or discount but just the description of the dish/dishes. We are strictly interested in offers or discounts. \n'
    'Step 5: Ensure that the generated report does not contain information that does not fall into a category mentioned in the previous steps. \n'
    'Step 6: Ensure that the generated report is written concisely, adding the following to each piece of information: the name of the page from which the information was extracted, the link to the post from which the information was extracted, and the city where the restaurant is located. \n'
    'Step 7: Ensure that the information found in the report is extracted only from the posts received in step 1. \n'
)

PROFILES_TEMPLATE_REFINE = (
    'You are a specialist in the HORECA field and have generated a report related to multiple posts from different pages. \n'
    'Report: {raport} \n'
    'The generated report is not concise enough and needs to follow a predefined structure. \n'
    "Let's go step by step: "
    'Step 1: Analyze the report you previously generated. \n'
    'Step 2: Adapt the report to the specified structure. \n'
    'The required structure is: {format_instructions} \n'
    'If there is no relevant information for one of the keys, you will leave it as an empty list. \n'
    'Your response should not contain ```json```; only the specified structure is allowed. \n'
)