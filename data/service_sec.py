import json
from edgar import Company, set_identity
import pandas as pd

set_identity("Adrian Wong ian57084@gmail.com")
company = Company("MSFT")


def get_company_profile(company):
    data = company.data
    business_address = company.business_address()
    mailing_address = company.mailing_address()

    return {
        "identification": {
            "cik": company.cik,
            "name": company.name,
            "display_name": company.display_name,
            "ticker": company.get_ticker(),
            "tickers": company.tickers,
            "exchanges": company.get_exchanges(),
            "not_found": company.not_found,
        },
        "classification": {
            "sic": company.sic,
            "sic_description": data.sic_description,
            "industry": company.industry,
            "entity_type": data.entity_type,
            "business_category": company.business_category,
            "category": data.category,
            "filer_category": company.filer_category,
            "filer_type": company.filer_type,
            "fiscal_year_end": company.fiscal_year_end,
            "is_company": data.is_company,
            "is_individual": data.is_individual,
            "is_bdc": data.is_bdc,
            "is_accelerated_filer": company.is_accelerated_filer,
            "is_large_accelerated_filer": company.is_large_accelerated_filer,
            "is_non_accelerated_filer": company.is_non_accelerated_filer,
            "is_smaller_reporting_company": company.is_smaller_reporting_company,
            "is_emerging_growth_company": company.is_emerging_growth_company,
            "is_foreign": company.is_foreign,
            "is_financial_institution": company.is_financial_institution(),
            "is_fund": company.is_fund(),
            "is_operating_company": company.is_operating_company(),
        },
        "registration": {
            "ein": data.ein,
            "state_of_incorporation": data.state_of_incorporation,
            "state_of_incorporation_description": (
                data.state_of_incorporation_description
            ),
            "former_names": data.former_names,
            "flags": data.flags,
            "reit_subtype": company.reit_subtype,
        },
        "contact": {
            "website": data.website,
            "investor_website": data.investor_website,
            "phone": data.phone,
        },
        "business_address": {
            "street1": business_address.street1,
            "street2": business_address.street2,
            "city": business_address.city,
            "state_or_country": business_address.state_or_country,
            "state_or_country_desc": business_address.state_or_country_desc,
            "zipcode": business_address.zipcode,
        } if business_address else None,
        "mailing_address": {
            "street1": mailing_address.street1,
            "street2": mailing_address.street2,
            "city": mailing_address.city,
            "state_or_country": mailing_address.state_or_country,
            "state_or_country_desc": mailing_address.state_or_country_desc,
            "zipcode": mailing_address.zipcode,
        } if mailing_address else None,
    }


import json
import pathlib
import pandas as pd

def parse_statement_to_dict(statement):
    """Helper function to convert any statement object into a nested dictionary."""
    df = statement.to_dataframe()
    statement_dict = {}
    stack = []

    for _, row in df.iterrows():
        label = row["label"]
        depth = int(row["depth"])
        is_abstract = row["is_abstract"]

        item = {} if is_abstract else {
            period: (
                None if pd.isna(row[period])
                else row[period].item()
                if hasattr(row[period], "item")
                else row[period]
            )
            for period in statement.periods
        }

        while stack and stack[-1][0] >= depth:
            stack.pop()

        if stack:
            stack[-1][1][label] = item
        else:
            statement_dict[label] = item

        stack.append((depth, item))

    return statement_dict


def get_financial_statement(company, statement_type, output_dir=None):
    """
    Generic function to fetch, parse, and optionally save any financial statement as JSON.
    
    Parameters:
    - company: the company object
    - statement_type (str): 'income_statement', 'balance_sheet', or 'cash_flow_statement'
    - output_dir (str or pathlib.Path, optional): Local folder path to save the JSON file.
    """
    # Dynamically get and execute the statement method
    statement_method = getattr(company, statement_type)
    statement = statement_method()
    
    # Parse into nested dictionary
    statement_dict = parse_statement_to_dict(statement)
    
    # Save to local folder if output_dir is provided
    if output_dir:
        dir_path = pathlib.Path(output_dir)
        # Create the directory if it doesn't already exist
        dir_path.mkdir(parents=True, exist_ok=True)
        
        file_path = dir_path / f"{statement_type}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(statement_dict, f, indent=4)
        print(f"Successfully saved to: {file_path}")
        
    return statement_dict


# This will fetch the income statement, parse it, and save it as 'income_statement.json' inside the 'financial_data' folder
income_data = get_financial_statement(company, "income_statement", output_dir="financial_data")

# This will fetch and save the balance sheet in the same folder
balance_data = get_financial_statement(company, "balance_sheet", output_dir="financial_data")

cashflow_data = get_financial_statement(company, "cash_flow_statement", output_dir="financial_data")