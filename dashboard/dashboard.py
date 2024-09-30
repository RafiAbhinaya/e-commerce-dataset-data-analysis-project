# import libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from datetime import datetime
sns.set(style='dark')

# define helper codes from EDA
def create_revenue_city_df(df):
    revenue_city_df = df.groupby('customer_city').agg({
        'total_price':'sum'
        }).reset_index()
    revenue_city_df.rename(columns={'customer_city':'city',
                            'total_price':'revenue'},
                            inplace=True)
    return revenue_city_df

def create_revenue_state_df(df):
    revenue_state_df = df.groupby('customer_state').agg({
        'total_price':'sum'
        }).reset_index()
    revenue_state_df.rename(columns={'customer_state':'state',
                            'total_price':'revenue'},
                            inplace=True)
    return revenue_state_df

def create_order_reviews_df(df):
    order_reviews_df = df.groupby('review_score').agg({
        'order_id':'nunique'
        })
    order_reviews_df.rename(columns={'order_id':'total_customers'}, inplace=True)
    
    return order_reviews_df

def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
       "order_purchase_timestamp": "max", # takes latest order date
       "order_id": "nunique", # calculates total order
        "total_price": "sum" # calculates total reveneu produced
        })

    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]

    # calculates when the customer last ordered (days)
    rfm_df["max_order_timestamp"] = pd.to_datetime(rfm_df['max_order_timestamp'])
    recent_date = datetime.strptime('2018-09-04', "%Y-%m-%d")
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    return rfm_df

# read csv
all_df = pd.read_csv('/dashboard/all_df.csv')

# sort by order date
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)

# change dtype to datetime 
all_df['order_purchase_timestamp'] = pd.to_datetime(all_df['order_purchase_timestamp'])

# assign oldest and latest order date
min_date = all_df['order_purchase_timestamp'].min()
max_date = all_df['order_purchase_timestamp'].max()

with st.sidebar:
    # subheader
    st.sidebar.title('Filter')

    # assign start_date and end_date from date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date,max_date]
        )
    
# assign star_date and end_date as filters for main_df
main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]

# create dataframes using helper function
revenue_city_df = create_revenue_city_df(main_df)
revenue_state_df = create_revenue_state_df(main_df)
order_reviews_df = create_order_reviews_df(main_df)
rfm_df = create_rfm_df(main_df)

# create header
st.header('E-Commerce Insights :shopping_bags:')

# create subheader
st.subheader('Revenue Demographics')

# create metric
total_revenue = round(revenue_city_df['revenue'].sum(),2)
st.metric('Total Revenue', total_revenue)

# create 2 canvas
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(30, 10))
colors = colors3 = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

# city barchart
sns.barplot(x='city',
            y='revenue',
            data=revenue_city_df.sort_values('revenue',ascending=False).head(5),
            palette=colors,
            ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By City", loc="center", fontsize=30)
ax[0].tick_params(axis ='x', labelsize=15)

# state barchart
sns.barplot(x='state',
            y='revenue',
            data=revenue_state_df.sort_values('revenue',ascending=False).head(5),
            palette=colors,
            ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By State", loc="center", fontsize=30)
ax[1].tick_params(axis ='x', labelsize=15)

# show charts
st.pyplot(fig)

# create subheader
st.subheader('Customer Satisfaction Percentage')

# create piechart
fig, ax = plt.subplots(figsize=(16,8))
colors = ["#E5F3F7", "#CEE8F0", "#B7DDE9", "#A0D2E2", "#89C7DB"]
labels = order_reviews_df.index

plt.pie(order_reviews_df['total_customers'],
        labels=labels,
        colors=colors,
        autopct='%1.1f%%',
        startangle=90
        )
plt.title('Customer Reviews Measured by Stars')
plt.legend(labels, loc = 'best', bbox_to_anchor = (1.0,1.0))

# show chart
st.pyplot(fig)

# create subheader
st.subheader('RFM Analysis')

# create canvases
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))
colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]

# create recency barchart
sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
ax[0].set_xticklabels(ax[0].get_xticklabels(), rotation=45)
ax[0].tick_params(axis ='x', labelsize=15)

# create frequency barchart
sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Frequency", loc="center", fontsize=18)
ax[1].set_xticklabels(ax[0].get_xticklabels(), rotation=45)
ax[1].tick_params(axis='x', labelsize=15)

# create monetary barchart
sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Monetary", loc="center", fontsize=18)
ax[2].set_xticklabels(ax[0].get_xticklabels(), rotation=45)
ax[2].tick_params(axis='x', labelsize=15)

plt.suptitle("Best Customer Based on RFM Parameters", fontsize=20)

# show chart
st.pyplot(fig)
