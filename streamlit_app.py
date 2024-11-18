import streamlit as st
import pandas as pd
import pydeck as pdk


# Sample data with cost per state for each Thanksgiving item
df = pd.read_csv("Marketing - Thanksgiving9.csv")

# Streamlit title
st.title("🧺 BetterBasket Interactive Holiday Meal Cost Map")

st.markdown('<p style="font-size:14px; font-style:italic; color:gray;">A visualization of total costs for Thanksgiving baskets based on most common grocery chain in the state</p>', unsafe_allow_html=True)


all_items = df.columns[4:]  # Assuming columns after "State" and "Grocery Store" are items

regular_items = [item for item in all_items if not item.endswith("- Private Label")]
private_label_items = {item.replace(" - Private Label", ""): item for item in all_items if item.endswith("- Private Label")}

# Assuming columns after "State" and "Grocery Store" are numeric
for col in df.columns[5:]:
    df[col] = pd.to_numeric(df[col], errors="coerce")  # Converts to numeric, setting invalid values to NaN

# Fill NaN values with 0 (optional, if missing data should default to 0)
df.fillna(0, inplace=True)



# Larger checkbox for private label toggle
st.sidebar.markdown("### **Private Label Option**")
private_label = st.sidebar.checkbox("Make All Items Private Label")


# Sidebar for item selection
st.sidebar.header("Select Thanksgiving Items to Add to Total Cost:")


if private_label:
    # Replace regular items with their private label versions
    selected_items = {
        private_label_items.get(item, item): st.sidebar.checkbox(item, value=True) for item in regular_items
    }
else:
    # Use only regular items
    selected_items = {
        item: st.sidebar.checkbox(item, value=True) for item in regular_items
    }


# Calculate total cost based on selected items
df["Total Cost"] = df.apply(
    lambda row: sum(row[item] for item in selected_items if selected_items[item]), axis=1
)

df["Total Cost Rounded"] = df["Total Cost"].round(2)


df["Cost_Text"] = df["Total Cost"].apply(lambda x: f"${x:,.2f}")  # Add dollar sign and format as currency


df["Cost_Scale"] = df["Total Cost"] / df["Total Cost"].max()  # Scale between 0 and 1


df["Total Cost Tooltip"] = df["Total Cost"].round(2)  # Round to two decimal places


scatter_layer = pdk.Layer(
   "ScatterplotLayer",
   data=df,
   get_position="[Longitude, Latitude]",
   get_color="[255 * Cost_Scale, 0, 255 * (1 - Cost_Scale), 160]",  # Gradient from purple to red
get_radius="Cost_Scale * 100000 + 5000",  # Scale size with a minimum radius
   pickable=True,
   extruded=True
)

text_layer = pdk.Layer(
    "TextLayer",
    data=df,
    get_position="[Longitude, Latitude]",
    get_text="Cost_Text",
    get_color=[0, 0, 0, 255],  # Black text
    get_size=10,  # Text size
    get_alignment_baseline="'top'",  # Position text below the dot
    get_anchor="'middle'",  # Center text horizontally
    get_pixel_offset="[0, -20]",  # Slight upward offset

    pickable=False
)


# View state for the map
view_state = pdk.ViewState(
    latitude=37.0902,
    longitude=-95.7129,
    zoom=4,
    pitch=0,
    bearing = 0
)




# Create the deck.gl map with dynamic tooltip
r = pdk.Deck(
    layers=[text_layer,scatter_layer],
    initial_view_state=view_state,
    tooltip={"text": "{State} ({Grocery Store}): ${Total Cost Tooltip}"},
    map_style="mapbox://styles/mapbox/light-v10"
)

# Display map in Streamlit
st.pydeck_chart(r)

# Prepare detailed summary for each state, chain, and basket
columns_order = ["State", "Grocery Store", "Total Cost"] + list(selected_items.keys())  # Reorder columns
detailed_summary = df[columns_order]


# Apply heatmap styling based on ranking within columns
heatmap_summary = detailed_summary.style.background_gradient(
    subset=["Total Cost"] + list(selected_items.keys()),  # Columns to apply gradient
    cmap="YlOrRd"  # Heatmap color scheme
)

# Format monetary columns to display dollar signs and two decimal places
formatted_summary = detailed_summary.style.format(
    subset=["Total Cost"] + list(selected_items.keys()),
    formatter=lambda x: f"${x:,.2f}"  # Dollar sign and two decimal places
).background_gradient(
    subset=["Total Cost"] + list(selected_items.keys()),  # Columns to apply gradient
    cmap="YlOrRd"  # Heatmap color scheme
)

# Display detailed summary
st.title("Detailed Summary of Each State's Basket:")
st.dataframe(formatted_summary)