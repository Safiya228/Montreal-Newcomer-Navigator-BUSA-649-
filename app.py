from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Montreal Newcomer Navigator",
    page_icon="🧭",
    layout="wide",
)
st.markdown(
    """
    <link
        rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"
    >
    <style>
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .badge {
        display: inline-block;
        padding: 0.32rem 0.75rem;
        border-radius: 999px;
        background: rgba(45, 212, 191, 0.12);
        border: 1px solid rgba(45, 212, 191, 0.4);
        color: #5eead4;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        text-transform: uppercase;
        margin-bottom: 0.6rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

NEIGHBORHOODS_PATH = Path(__file__).with_name("Montreal_Newcomer_Navigator_Scored.csv")
CAMPUS_DISTANCES_PATH = Path(__file__).with_name("Neighborhood_Campus_Distances.csv")

st.markdown(
    """
    <style>
    /* ---------- Global layout ---------- */
    .block-container {
        max-width: 1360px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    h1, h2, h3, h4 {
        font-weight: 700;
        letter-spacing: -0.01em;
        color: #f1f5f9;
    }

    p, li, span, label {
        color: #cbd5e1;
    }

    /* ---------- Hero ---------- */
    .hero {
        padding: 3.25rem 3rem;
        border-radius: 20px;
        margin-bottom: 2.25rem;
        background:
            radial-gradient(
                circle at top right,
                rgba(255, 255, 255, 0.12),
                transparent 45%
            ),
            linear-gradient(
                120deg,
                #0f2540 0%,
                #14375e 45%,
                #0d5c63 100%
            );
        color: #f5f7fa;
        box-shadow: 0 12px 32px rgba(15, 37, 64, 0.18);
    }

    .hero h1 {
        font-size: 2.65rem;
        line-height: 1.15;
        margin: 0.6rem 0 1rem 0;
        max-width: 820px;
        color: #ffffff;
        font-weight: 800;
    }

    .hero p {
        font-size: 1.08rem;
        max-width: 720px;
        opacity: 0.88;
        color: #eef1f5;
    }

    .hero-badge {
        display: inline-block;
        padding: 0.35rem 0.85rem;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.28);
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        color: #eef1f5;
    }

    /* ---------- Metrics ---------- */
    div[data-testid="stMetric"] {
        background: #1c2536;
        border: 1px solid #2e3a52;
        border-radius: 14px;
        padding: 0.9rem 1rem 0.6rem 1rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.25);
    }

    div[data-testid="stMetricValue"] {
        color: #2dd4bf;
        font-weight: 700;
    }

    div[data-testid="stMetricLabel"] {
        color: #cbd5e1;
    }

    /* ---------- Containers / cards ---------- */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #1c2536 !important;
        border-radius: 16px !important;
        border-color: #2e3a52 !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.25);
    }

    /* ---------- Tabs ---------- */
    button[data-baseweb="tab"] {
        font-size: 0.95rem;
        font-weight: 600;
        padding: 0.6rem 1.1rem;
    }

    /* ---------- Buttons ---------- */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(120deg, #0d5c63, #14375e);
        border: none;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.65rem 1.4rem;
        box-shadow: 0 4px 14px rgba(13, 92, 99, 0.25);
    }

    div.stButton > button[kind="primary"]:hover {
        opacity: 0.92;
    }
    </style>
    """,
    unsafe_allow_html=True,
)



@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not NEIGHBORHOODS_PATH.exists():
        raise FileNotFoundError(
            f"Missing file: {NEIGHBORHOODS_PATH.name}. "
            "Place it in the same folder as app.py."
        )

    if not CAMPUS_DISTANCES_PATH.exists():
        raise FileNotFoundError(
            f"Missing file: {CAMPUS_DISTANCES_PATH.name}. "
            "Place it in the same folder as app.py."
        )

    df = pd.read_csv(NEIGHBORHOODS_PATH)
    campus_df = pd.read_csv(CAMPUS_DISTANCES_PATH)

    numeric_cols = [
        "Transit_Score_0_100",
        "Affordability_Score_0_100",
        "Amenity_Score_0_100",
        "Current_Usability_Score_0_100",
        "Transit_Stop_Count",
        "Metro_Station_Count",
        "Cafe_Count",
        "Grocery_Count",
        "Library_Count",
        "Park_Count",
        "Gym_Count",
        "Centroid_Lat",
        "Centroid_Lon",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    campus_df["Distance_km"] = pd.to_numeric(campus_df["Distance_km"], errors="coerce")
    campus_df["Campus_Access_Score_0_100"] = pd.to_numeric(
        campus_df["Campus_Access_Score_0_100"], errors="coerce"
    )
    return df, campus_df


try:
    df, campus_df = load_data()
except (FileNotFoundError, pd.errors.ParserError) as error:
    st.error(str(error))
    st.stop()

campus_options = sorted(campus_df["Campus"].dropna().unique().tolist())

st.markdown(
    """
    <div class="hero">
        <div class="hero-badge">Built for newcomers to Montreal</div>
        <h1>Find the Montreal neighborhood that fits your life</h1>
        <p>
            Compare neighborhoods by commute, affordability, transit access,
            and everyday amenities.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


summary1, summary2, summary3, summary4 = st.columns(4)

with summary1:
    st.metric("Neighborhoods", len(df))

with summary2:
    st.metric("Campuses & workplaces", len(campus_options))

with summary3:
    st.metric("Scoring dimensions", 4)

with summary4:
    st.metric("Top matches shown", 5)

st.markdown("## How it works")
st.caption(
    "Choose your destination, set your priorities, "
    "and explore your personalized matches."
)

step1, step2, step3 = st.columns(3)

with step1:
    with st.container(border=True):
        st.markdown("### 1. Choose your destination")
        st.write(
            "Select your campus or workplace and preferred commute distance."
        )

with step2:
    with st.container(border=True):
        st.markdown("### 2. Set your priorities")
        st.write(
            "Adjust the importance of transit, campus access, "
            "affordability, and amenities."
        )

with step3:
    with st.container(border=True):
        st.markdown("### 3. Explore your matches")
        st.write(
            "Review recommendations, compare areas, and view them on the map."
        )

tab1, tab2, tab3 = st.tabs(
    [
        "✨ Get recommendations",
        "🗺️ Explore the map",
        "💬 Ask the navigator",
    ]
)

with tab1:
    st.subheader("What matters most to you?")

    # ---------------------------------------------------------
    # Filters
    # ---------------------------------------------------------
    with st.container(border=True):
        st.markdown("### Tell us what matters to you")

        col1, col2, col3 = st.columns(3)

        with col1:
            default_campus = (
                campus_options.index("McGill Downtown Campus")
                if "McGill Downtown Campus" in campus_options
                else 0
            )

            selected_campus = st.selectbox(
                "Your campus or workplace",
                campus_options,
                index=default_campus,
            )

        with col2:
            environment = st.selectbox(
                "Preferred environment",
                ["Any"]
                + sorted(
                    df["Environment_Type"]
                    .dropna()
                    .unique()
                    .tolist()
                ),
            )

        with col3:
            max_distance = st.slider(
                "Maximum approximate distance to campus (km)",
                min_value=1,
                max_value=30,
                value=15,
            )

    # ---------------------------------------------------------
    # Priority weights
    # ---------------------------------------------------------
    with st.container(border=True):
        st.markdown("### Set your priorities")

        st.caption(
            "The sliders do not need to total 100. "
            "The app normalizes them automatically."
        )

        w1, w2, w3, w4 = st.columns(4)

        with w1:
            transit_weight = st.slider(
                "🚇 Transit",
                min_value=0,
                max_value=100,
                value=25,
            )

        with w2:
            campus_weight = st.slider(
                "🎓 Campus proximity",
                min_value=0,
                max_value=100,
                value=25,
            )

        with w3:
            affordability_weight = st.slider(
                "🏠 Affordability",
                min_value=0,
                max_value=100,
                value=25,
            )

        with w4:
            amenity_weight = st.slider(
                "☕ Amenities",
                min_value=0,
                max_value=100,
                value=25,
            )

    find_matches_clicked = st.button(
        "✨ Find my matches",
        type="primary",
        use_container_width=True,
    )

    if find_matches_clicked:
        st.session_state["has_matches"] = True

    find_matches = st.session_state.get("has_matches", False)

    if not find_matches:
        st.info(
            "Choose your preferences above, then click "
            "'Find my matches' to see recommendations."
        )

    if find_matches:
        # ---------------------------------------------------------
        # Join selected-campus scores
        # ---------------------------------------------------------
        campus_slice = campus_df[
            campus_df["Campus"] == selected_campus
        ][
            [
                "Neighborhood",
                "Distance_km",
                "Campus_Access_Score_0_100",
            ]
        ].rename(
            columns={
                "Distance_km": "Distance_to_Selected_Campus_km",
                "Campus_Access_Score_0_100":
                    "Selected_Campus_Access_Score_0_100",
            }
        )

        working = df.merge(
            campus_slice,
            on="Neighborhood",
            how="left",
        )

        # ---------------------------------------------------------
        # Apply filters
        # ---------------------------------------------------------
        if environment != "Any":
            working = working[
                working["Environment_Type"] == environment
            ]

        working = working[
            working["Distance_to_Selected_Campus_km"]
            .fillna(float("inf"))
            <= max_distance
        ].copy()

        # ---------------------------------------------------------
        # Personalized score
        # ---------------------------------------------------------
        total_weight = (
            transit_weight
            + campus_weight
            + affordability_weight
            + amenity_weight
        )

        if total_weight == 0:
            transit_weight = 25
            campus_weight = 25
            affordability_weight = 25
            amenity_weight = 25
            total_weight = 100

        working["Personalized_Score"] = (
            working["Transit_Score_0_100"].fillna(0)
            * transit_weight
            + working[
                "Selected_Campus_Access_Score_0_100"
            ].fillna(0)
            * campus_weight
            + working[
                "Affordability_Score_0_100"
            ].fillna(0)
            * affordability_weight
            + working[
                "Amenity_Score_0_100"
            ].fillna(0)
            * amenity_weight
        ) / total_weight

        results = (
            working.sort_values(
                "Personalized_Score",
                ascending=False,
            )
            .head(5)
            .copy()
        )

        st.caption(
            "Effective priorities — "
            f"Transit: {transit_weight / total_weight:.0%}, "
            f"Campus: {campus_weight / total_weight:.0%}, "
            f"Affordability: "
            f"{affordability_weight / total_weight:.0%}, "
            f"Amenities: {amenity_weight / total_weight:.0%}"
        )

        # ---------------------------------------------------------
        # Results
        # ---------------------------------------------------------
        st.markdown("## Top recommendations")

        if results.empty:
            st.warning(
                "No areas match the selected filters. "
                "Try increasing the maximum distance or selecting "
                "'Any' environment."
            )

        else:
            for rank, (_, row) in enumerate(
                results.iterrows(),
                start=1,
            ):
                with st.container(border=True):
                    left, middle, right = st.columns(
                        [3.2, 1.15, 1.15]
                    )

                    with left:
                        if rank == 1:
                            st.markdown(
                                '<span class="badge">'
                                '⭐ Best match'
                                '</span>',
                                unsafe_allow_html=True,
                            )

                        st.markdown(
                            f"### {rank}. {row['Neighborhood']}"
                        )

                        st.write(
                            f"📍 **Environment:** "
                            f"{row['Environment_Type']}  \n"
                            f"🎓 **Approximate distance to "
                            f"{selected_campus}:** "
                            f"{row['Distance_to_Selected_Campus_km']:.1f} km"
                        )

                        reason_parts = []

                        if (
                            row["Transit_Score_0_100"]
                            >= 55
                        ):
                            reason_parts.append(
                                "strong transit access"
                            )

                        if (
                            row[
                                "Selected_Campus_Access_Score_0_100"
                            ]
                            >= 70
                        ):
                            reason_parts.append(
                                "close to your campus"
                            )

                        if (
                            row[
                                "Affordability_Score_0_100"
                            ]
                            >= 70
                        ):
                            reason_parts.append(
                                "relatively affordable"
                            )

                        if (
                            row["Amenity_Score_0_100"]
                            >= 70
                        ):
                            reason_parts.append(
                                "good access to amenities"
                            )

                        if (
                            pd.notna(
                                row["Metro_Station_Count"]
                            )
                            and row["Metro_Station_Count"] > 0
                        ):
                            reason_parts.append(
                                f"{int(row['Metro_Station_Count'])} "
                                "metro station(s)"
                            )

                        reason = (
                            ", ".join(reason_parts)
                            or "a balanced combination of indicators"
                        )

                        st.caption(
                            f"Why it ranks well: {reason}."
                        )

                        # -----------------------------------------
                        # Progress bars
                        # -----------------------------------------
                        st.markdown("#### Score breakdown")

                        transit_score = int(
                            max(
                                0,
                                min(
                                    100,
                                    round(
                                        float(
                                            row[
                                                "Transit_Score_0_100"
                                            ]
                                        )
                                    ),
                                ),
                            )
                        )

                        affordability_score = int(
                            max(
                                0,
                                min(
                                    100,
                                    round(
                                        float(
                                            row[
                                                "Affordability_Score_0_100"
                                            ]
                                        )
                                    ),
                                ),
                            )
                        )

                        amenity_score = int(
                            max(
                                0,
                                min(
                                    100,
                                    round(
                                        float(
                                            row[
                                                "Amenity_Score_0_100"
                                            ]
                                        )
                                    ),
                                ),
                            )
                        )

                        campus_access_score = int(
                            max(
                                0,
                                min(
                                    100,
                                    round(
                                        float(
                                            row[
                                                "Selected_Campus_Access_Score_0_100"
                                            ]
                                        )
                                    ),
                                ),
                            )
                        )

                        st.caption(
                            f"🚇 Transit: "
                            f"{row['Transit_Score_0_100']:.1f}/100"
                        )
                        st.progress(transit_score)

                        st.caption(
                            f"🎓 Campus access: "
                            f"{row['Selected_Campus_Access_Score_0_100']:.1f}/100"
                        )
                        st.progress(campus_access_score)

                        st.caption(
                            f"🏠 Affordability: "
                            f"{row['Affordability_Score_0_100']:.1f}/100"
                        )
                        st.progress(affordability_score)

                        st.caption(
                            f"☕ Amenities: "
                            f"{row['Amenity_Score_0_100']:.1f}/100"
                        )
                        st.progress(amenity_score)

                    with middle:
                        st.metric(
                            "Overall match",
                            f"{row['Personalized_Score']:.1f}/100",
                        )

                        st.metric(
                            "Transit",
                            f"{row['Transit_Score_0_100']:.1f}",
                        )

                        st.metric(
                            "Campus access",
                            f"{row['Selected_Campus_Access_Score_0_100']:.1f}",
                        )

                    with right:
                        st.metric(
                            "Affordability",
                            f"{row['Affordability_Score_0_100']:.1f}",
                        )

                        st.metric(
                            "Amenities",
                            f"{row['Amenity_Score_0_100']:.1f}",
                        )

                        st.metric(
                            "Distance",
                            f"{row['Distance_to_Selected_Campus_km']:.1f} km",
                        )

            # -----------------------------------------------------
            # Recommendation map
            # -----------------------------------------------------
            st.markdown("## Recommended areas on the map")

            results_map = results.dropna(
                subset=[
                    "Centroid_Lat",
                    "Centroid_Lon",
                ]
            ).copy()

            if results_map.empty:
                st.warning(
                    "No valid coordinates are available "
                    "for the recommended areas."
                )

            else:
                results_map["Map_Marker_Size"] = (
                    results_map["Personalized_Score"]
                    .fillna(0)
                    .clip(lower=1)
                    .pow(0.5)
                )

                recommendation_map = px.scatter_mapbox(
                    results_map,
                    lat="Centroid_Lat",
                    lon="Centroid_Lon",
                    size="Map_Marker_Size",
                    color="Personalized_Score",
                    hover_name="Neighborhood",
                    hover_data={
                        "Environment_Type": True,
                        "Personalized_Score": ":.1f",
                        "Distance_to_Selected_Campus_km": ":.1f",
                        "Transit_Score_0_100": ":.1f",
                        "Selected_Campus_Access_Score_0_100": ":.1f",
                        "Affordability_Score_0_100": ":.1f",
                        "Amenity_Score_0_100": ":.1f",
                        "Map_Marker_Size": False,
                        "Centroid_Lat": False,
                        "Centroid_Lon": False,
                    },
                    zoom=10,
                    height=520,
                    size_max=32,
                )

                recommendation_map.update_layout(
                    mapbox_style="open-street-map",
                    mapbox_center={
                        "lat": 45.5019,
                        "lon": -73.5674,
                    },
                    coloraxis_colorbar_title="Match score",
                    margin={
                        "r": 0,
                        "t": 0,
                        "l": 0,
                        "b": 0,
                    },
                )

                st.plotly_chart(
                    recommendation_map,
                    use_container_width=True,
                    config={
                        "scrollZoom": True,
                        "displaylogo": False,
                    },
                )

                st.caption(
                    "The markers show approximate neighborhood "
                    "centroids, not complete neighborhood boundaries."
                )
with tab2:
    st.subheader("Explore Montreal neighborhoods")

    metric_labels = {
        "Overall usability": "Current_Usability_Score_0_100",
        "Transit score": "Transit_Score_0_100",
        "Affordability score": "Affordability_Score_0_100",
        "Amenity score": "Amenity_Score_0_100",
        "Transit-stop count": "Transit_Stop_Count",
        "Metro-station count": "Metro_Station_Count",
    }

    selected_metric_label = st.selectbox(
        "Color neighborhoods by",
        list(metric_labels.keys()),
    )

    metric = metric_labels[selected_metric_label]

    map_df = df.dropna(
        subset=["Centroid_Lat", "Centroid_Lon"]
    ).copy()

    if map_df.empty:
        st.warning("No valid neighborhood coordinates were found.")
    else:
        map_df["Map_Marker_Size"] = (
            map_df["Transit_Stop_Count"]
            .fillna(0)
            .clip(lower=1)
            .pow(0.5)
        )

        fig = px.scatter_mapbox(
            map_df,
            lat="Centroid_Lat",
            lon="Centroid_Lon",
            size="Map_Marker_Size",
            color=metric,
            hover_name="Neighborhood",
            hover_data={
                "Environment_Type": True,
                "Transit_Stop_Count": True,
                "Metro_Station_Count": True,
                "Cafe_Count": True,
                "Grocery_Count": True,
                "Library_Count": True,
                "Park_Count": True,
                "Gym_Count": True,
                "Map_Marker_Size": False,
                "Centroid_Lat": False,
                "Centroid_Lon": False,
            },
            zoom=9.5,
            height=620,
            size_max=30,
        )

        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox_center={
                "lat": 45.5019,
                "lon": -73.5674,
            },
            coloraxis_colorbar_title=selected_metric_label,
            margin={
                "r": 0,
                "t": 0,
                "l": 0,
                "b": 0,
            },
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "scrollZoom": True,
                "displaylogo": False,
            },
        )

    st.caption(
        "This marker map uses approximate neighborhood centroids, "
        "not filled neighborhood boundaries."
    )

    st.markdown("### Neighborhood comparison")

    selected = st.multiselect(
        "Select up to 5 neighborhoods",
        sorted(df["Neighborhood"].dropna().tolist()),
        max_selections=5,
    )

    if selected:
        comparison_cols = [
            "Neighborhood",
            "Environment_Type",
            "Transit_Stop_Count",
            "Metro_Station_Count",
            "Cafe_Count",
            "Grocery_Count",
            "Library_Count",
            "Park_Count",
            "Gym_Count",
            "Transit_Score_0_100",
            "Affordability_Score_0_100",
            "Amenity_Score_0_100",
            "Current_Usability_Score_0_100",
        ]

        st.dataframe(
            df[df["Neighborhood"].isin(selected)][comparison_cols],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info(
            "Select neighborhoods above to compare their scores and amenities."
        )

with tab3:
    st.subheader("Ask the Montreal Navigator")

    st.caption(
        "Ask about transit, affordability, amenities, "
        "or a specific Montreal neighborhood."
    )
    st.caption(
        "This assistant uses predefined rules and the project dataset."
    )

    prompt1, prompt2, prompt3 = st.columns(3)

    with prompt1:
        st.info("Which neighborhoods have the best transit?")

    with prompt2:
        st.info("Which areas are most affordable?")

    with prompt3:
        st.info("Tell me about Verdun.")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hello! Ask me about Montreal neighborhoods. "
                    "For example: Which areas have the best transit?"
                ),
            }
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    question = st.chat_input(
        "Ask about Montreal neighborhoods..."
    )

    if question:
        st.session_state.messages.append(
            {
                "role": "user",
                "content": question,
            }
        )

        with st.chat_message("user"):
            st.write(question)

        question_lower = question.lower()

        matched_neighborhoods = [
            neighborhood
            for neighborhood in df["Neighborhood"].dropna()
            if neighborhood.lower() in question_lower
        ]

        if "best transit" in question_lower:
            top_areas = df.nlargest(
                5,
                "Transit_Score_0_100",
            )

            answer = (
                "The neighborhoods with the highest transit scores are: "
                + ", ".join(
                    [
                        f"{row['Neighborhood']} "
                        f"({row['Transit_Score_0_100']:.1f})"
                        for _, row in top_areas.iterrows()
                    ]
                )
                + "."
            )

        elif (
            "affordable" in question_lower
            or "cheapest" in question_lower
        ):
            top_areas = df.nlargest(
                5,
                "Affordability_Score_0_100",
            )

            answer = (
                "The neighborhoods with the highest affordability scores are: "
                + ", ".join(
                    [
                        f"{row['Neighborhood']} "
                        f"({row['Affordability_Score_0_100']:.1f})"
                        for _, row in top_areas.iterrows()
                    ]
                )
                + "."
            )

        elif (
            "amenities" in question_lower
            or "cafes" in question_lower
            or "cafés" in question_lower
        ):
            top_areas = df.nlargest(
                5,
                "Amenity_Score_0_100",
            )

            answer = (
                "The neighborhoods with the highest amenity scores are: "
                + ", ".join(
                    [
                        f"{row['Neighborhood']} "
                        f"({row['Amenity_Score_0_100']:.1f})"
                        for _, row in top_areas.iterrows()
                    ]
                )
                + "."
            )

        elif len(matched_neighborhoods) == 1:
            neighborhood = matched_neighborhoods[0]

            row = df[
                df["Neighborhood"] == neighborhood
            ].iloc[0]

            answer = (
                f"{neighborhood} is classified as "
                f"{row['Environment_Type']}. "
                f"Its transit score is "
                f"{row['Transit_Score_0_100']:.1f}, "
                f"affordability score is "
                f"{row['Affordability_Score_0_100']:.1f}, "
                f"and amenity score is "
                f"{row['Amenity_Score_0_100']:.1f}."
            )

        else:
            answer = (
                "I can currently answer questions about the best transit, "
                "most affordable neighborhoods, amenities, "
                "or a specific neighborhood."
            )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

        with st.chat_message("assistant"):
            st.write(answer)
