# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(" Choose the fruits you want in your custom Smoothie! ")

name_on_order = st.text_input('Name on Smoothie: ')
st.write("The name on your Smoothie will be", name_on_order)

# option = st.selectbox(
#     "What is your favorite fruit?",
#     ("Banana", "Strawberries", "Peaches"))

# st.write("Your favorite fruit is:", option)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"),col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
ingredients_list=st.multiselect(
   'Choose up to 5 ingredients:'
     , my_dataframe
     , max_selections=5
    )
if ingredients_list:
   #st.write(ingredients_list)
   #st.text(ingredients_list)
   INGREDIENTS_STRING=''
   for fruit_chosen in ingredients_list:
       INGREDIENTS_STRING += fruit_chosen + ' '
   #st.write(INGREDIENTS_STRING)
   my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
           values ('""" + INGREDIENTS_STRING + """', '""" +name_on_order + """')"""
   #st.write(my_insert_stmt)
   #st.stop()
   time_to_insert = st.button('Submit Order')
   if time_to_insert:
       session.sql(my_insert_stmt).collect()
       st.success('Your Smoothie is ordered!', icon="✅")
