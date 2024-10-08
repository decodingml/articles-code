from pydantic import BaseModel, Field


class InformationProfiles(BaseModel):
    name: str = Field(description='Name of the page from where the information was extracted')
    information: str = Field(description='Information extracted for the specified key.')
    link: str = Field(description='Link of the post from where the information was extracted.')
    city: str = Field(description='City of the restaurant.')


class FieldProfiles(BaseModel):
    name: str = Field(description='Name of the key. Available options are: Giveaways, Deals and Discounts, Events.')
    keys: list[InformationProfiles] = Field(description='List of restaurants and the information given about them.')


class ReportProfiles(BaseModel):
    name: str = Field(description='Name of the report: REPORT RESTAURANTS NEWS')
    fields: list[FieldProfiles] = Field(description='List of all relevant keys for this report.')
