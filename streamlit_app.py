# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col
from urllib.parse import quote

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input('Name on Smoothie:')
st.write("The name on your Smoothie will be", name_on_order)

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"), col('SEARCH_ON'))
st.dataframe(data=my_dataframe,use_container_width=True)

# Convert Snowpark dataframe to pandas dataframe
pd_df = my_dataframe.to_pandas()

# ✅ FIXED: Use a list of values for multiselect
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # ✅ FIXED: Get SEARCH_ON value
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        if search_on:
            # ✅ FIXED: URL encode search value to avoid errors
            search_on_encoded = quote(search_on)

            # ✅ FIXED: Handle request response properly
            api_url = f"https://fruityvice.com/api/fruit/{search_on_encoded}"
            response = requests.get(api_url)

            if response.status_code == 200:
                fruit_data = response.json()

                # Ensure response is a dictionary or list
                if isinstance(fruit_data, dict):
                    fv_df = pd.DataFrame([fruit_data])
                elif isinstance(fruit_data, list):
                    fv_df = pd.DataFrame(fruit_data)
                else:
                    st.error("Invalid API response format")

                # Display data
                st.subheader(f"{fruit_chosen} Nutrition Information")
                st.dataframe(fv_df, use_container_width=True)
            else:
                st.error(f"Failed to fetch data for {search_on} (Status code: {response.status_code})")

    # ✅ FIXED: Use parameterized query to avoid SQL injection
    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.sql(
            "INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES (?, ?)",
            [ingredients_string.strip(), name_on_order]
        ).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
