import streamlit as st
import pandas as pd
import pydeck as pdk

# Sample data with cost per state for each Thanksgiving item
data = {
    "State": ["California", "Texas", "New York"],
    "Chain": ["Safeway", "HEB", "Wegmans"],
    "Latitude": [36.7783, 31.9686, 40.7128],
    "Longitude": [-119.4179, -99.9018, -74.0060],
    "Turkey": [27.86, 20.00, 40.34],
    "Cranberry 14 fl oz": [3.50, 2.06, 2.89],
    "Brown Gravy 0.87 fl oz": [1.25, 0.33, 0.99],
    "Peas 14.5 oz": [1.50, 0.52, 1.19]
}
df = pd.DataFrame(data)

# Streamlit title
st.title("Interactive Holiday Meal Cost Map")


# Larger checkbox for private label toggle
st.sidebar.markdown("### **Private Label Option**")
private_label = st.sidebar.checkbox("Make All Items Private Label")


# Sidebar for item selection
st.sidebar.header("Select Thanksgiving Items to Add to Total Cost:")
items = ["Turkey", "Cranberry 14 fl oz", "Brown Gravy 0.87 fl oz", "Peas 14.5 oz"]
selected_items = {item: st.sidebar.checkbox(item, value=True) for item in items}

# Calculate total cost based on selected items
df["Total Cost"] = df.apply(
    lambda row: sum(row[item] for item in selected_items if selected_items[item]), axis=1
)


# Pydeck layer for scatterplot with updated total cost
layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position="[Longitude, Latitude]",
    get_color="[200, 30, 0, 160]",
    get_radius=100000,
    pickable=True,
    extruded=True
)

# View state for the map
view_state = pdk.ViewState(
    latitude=37.0902,
    longitude=-95.7129,
    zoom=4,
    pitch=50
)

# Create the deck.gl map with dynamic tooltip
r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "{State} ({Chain}): ${Total Cost}"}
)

# Display map in Streamlit
st.pydeck_chart(r)

# Prepare detailed summary for each state, chain, and basket
detailed_summary = df[["State", "Chain"] + list(selected_items.keys()) + ["Total Cost"]]

# Display detailed summary
st.write("Detailed Summary of Each State's Basket:")
st.write(detailed_summary)