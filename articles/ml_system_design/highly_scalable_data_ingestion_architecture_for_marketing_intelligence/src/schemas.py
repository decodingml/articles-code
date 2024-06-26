from pydantic import BaseModel, Field


class InformationProfiles(BaseModel):
    name: str = Field(description='The name of the page from which the information is extracted.')
    information: str = Field(description='The specific information extracted for the specified key.')
    link: str = Field(description='The link to the post from where the information was extracted.')
    city: str = Field(description='The city where the restaurant is located.')


class FieldProfiles(BaseModel):
    name: str = Field(
        description='The name of the key. Categories always include: Giveaways, Deals and Discounts, Offers, Events.')
    keys: list[InformationProfiles] = Field(
        description='The list containing the restaurants and relevant information found.')


class ReportProfiles(BaseModel):
    name: str = Field(description='The name of the report, which is: RESTAURANT EVENTS REPORT')
    fields: list[FieldProfiles] = Field(
        description='The list containing all the keys with relevant information for this report.')
