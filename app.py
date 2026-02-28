import streamlit as st
from streamlit_option_menu import option_menu
from supabase import create_client, Client
import google.generativeai as genai
import pandas as pd
import datetime, random, requests
from bs4 import BeautifulSoup

# --- 1. DATABASE & PAGE CONFIG ---
URL = "https://fbsgqizdahbkleggxmgr.supabase.co"
KEY = "sb_publishable_nT8chJtNKJpUcAj9iuIhUg_Wxo7uGMM"
supabase: Client = create_client(URL, KEY)

st.set_page_config(page_title="PrePeak Pro Enterprise", layout="wide")

# Initialize Session States to prevent crashes
if 'auth' not in st.session_state: st.session_state.auth = False
if 'auth_mode' not in st.session_state: st.session_state.auth_mode = 'login'
if 'name' not in st.session_state: st.session_state.name = "Partner"
if 'ship_cost' not in st.session_state: st.session_state.ship_cost = 50.0
if 'ad_cost' not in st.session_state: st.session_state.ad_cost = 150.0
if 'pkg_cost' not in st.session_state: st.session_state.pkg_cost = 20.0

# --- 2. THE PROFESSIONAL AUTH ENGINE ---
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #1E88E5;'>🚀 PrePeak Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Get to know before they know</p>", unsafe_allow_html=True)
    
    _, main_col, _ = st.columns([1, 2, 1])
    
    with main_col:
        # --- SCREEN: LOGIN ---
        if st.session_state.auth_mode == 'login':
            st.subheader("Member Login")
            l_email = st.text_input("Email Address", placeholder="name@example.com")
            l_pass = st.text_input("Password", type="password", placeholder="••••••••")
            
            if st.button("Access Dashboard", use_container_width=True, type="primary"):
                try:
                    # Real Supabase Authentication
                    res = supabase.auth.sign_in_with_password({"email": l_email, "password": l_pass})
                    st.session_state.auth = True
                    st.session_state.user = l_email
                    # Fetch user's name from profiles table
                    p = supabase.table("profiles").select("full_name").eq("email", l_email).single().execute()
                    st.session_state.name = p.data['full_name']
                    st.rerun()
                except: st.error("Invalid credentials. Please try again.")

            st.markdown("<p style='text-align: center; margin: 15px 0; color: gray;'>— or —</p>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            c1.button("🔴 Google", use_container_width=True)
            c2.button("🔵 Facebook", use_container_width=True)
            
            st.write("---")
            if st.button("New Partner? Create an Account"):
                st.session_state.auth_mode = 'signup'
                st.rerun()

        # --- SCREEN: SIGN UP ---
        else:
            st.subheader("✨ Start 30-Day Free Trial")
            st.caption("Connect your store to unlock the profit-share model.")
            u_name = st.text_input("Name", placeholder="Your Name ...")
            u_email = st.text_input("Email", placeholder="you@gmail.com")
            u_pass = st.text_input("Create Password", type="password")
            u_store = st.text_input("Store URL", placeholder="brand.myshopify.com")
            
            if st.button("Activate My 30-Day Trial", use_container_width=True, type="primary"):
                if u_email and u_pass and u_store:
                    try:
                        # 1. Create Supabase User
                        supabase.auth.sign_up({"email": u_email, "password": u_pass})
                        # 2. Save detailed profile
                        trial_end = datetime.date.today() + datetime.timedelta(days=30)
                        supabase.table("profiles").insert({
                            "full_name": u_name, "email": u_email, 
                            "store_url": u_store, "trial_ends_at": str(trial_end)
                        }).execute()
                        st.balloons()
                        st.success("Registration Successful! Redirecting to Login...")
                        st.session_state.auth_mode = 'login'
                        st.rerun()
                    except Exception as e: st.error(f"Error: {str(e)}")
                else: st.warning("All fields are required to activate the trial.")
            
            st.write("---")
            if st.button("Already a Partner? Login here"):
                st.session_state.auth_mode = 'login'
                st.rerun()
    st.stop()

# --- 3. THE MAIN DASHBOARD (AFTER LOGIN) ---
with st.sidebar:
    st.title(f"👋 Hi, {st.session_state.name}")
    st.caption(f"User: {st.session_state.user}")
    ai_key = st.text_input("Gemini API Key", type="password", help="Needed for Ad Factory")
    if st.button("Log Out"):
        st.session_state.auth = False
        st.rerun()

selected = option_menu(
    menu_title=None,
    options=["Market Scout", "Financial Oracle", "Ad Factory", "Store Settings", "Owner Dashboard"],
    icons=["search", "calculator", "magic", "gear", "person-badge"],
    orientation="horizontal"
)

# --- 4. FEATURE: MARKET SCOUT ---
if selected == "Market Scout":
    st.header("🔍 Market & Competitor Intelligence")
    col_a, col_b = st.columns([2, 1])
    with col_a:
        url = st.text_input("🔗 Spy on Competitor Link (Amazon/Shopify)")
        start_d, end_d = st.date_input("Forecast Range", [datetime.date.today(), datetime.date.today() + datetime.timedelta(days=90)])
    with col_b:
        st.subheader("SEO Growth Forecast")
        delta = (end_d - start_d).days
        vol = random.randint(4000, 12000)
        proj = int(vol * (1.002 ** delta))
        st.metric(f"Projected Searches", f"{proj:,}")
        st.line_chart(pd.DataFrame([vol, proj], index=["Current", "Forecast"]))

# --- 5. FEATURE: FINANCIAL ORACLE (THE 10% MODEL) ---
elif selected == "Financial Oracle":
    st.header("💰 Net Profit-Share Engine")
    st.info(f"Applying Global Costs: Shipping (₹{st.session_state.ship_cost}), Ads (₹{st.session_state.ad_cost}), Pkg (₹{st.session_state.pkg_cost})")
    
    col1, col2 = st.columns(2)
    p_cost = col1.number_input("Unit Product Cost (₹)", value=500.0)
    s_price = col1.number_input("Sale Price (₹)", value=1500.0)
    units = col2.number_input("Monthly Units Sold", value=100)
    
    # MATH LOGIC
    total_rev = s_price * units
    total_exp = (p_cost + st.session_state.ship_cost + st.session_state.ad_cost + st.session_state.pkg_cost) * units
    net_profit = total_rev - total_exp
    prepeak_fee = net_profit * 0.10 if net_profit > 0 else 0
    
    st.markdown("---")
    r1, r2, r3 = st.columns(3)
    r1.metric("Gross Revenue", f"₹{total_rev:,.2f}")
    r2.metric("Net Profit", f"₹{net_profit:,.2f}")
    r3.metric("PrePeak Partner Fee (10%)", f"₹{prepeak_fee:,.2f}")
    
    if st.button("🚀 Lock & Sync Commission", type="primary", use_container_width=True):
        try:
            supabase.table("user_tracking").insert({"email": st.session_state.user, "profit": net_profit, "commission": prepeak_fee}).execute()
            st.success("Commission data synced to secure vault.")
        except Exception as e: st.error(f"Sync error: {str(e)}")

# --- 6. FEATURE: AD FACTORY (AI CREATIVES) ---
elif selected == "Ad Factory":
    st.header("🧠 AI Ad Creative Lab")
    ad_type = st.radio("Creative Format:", ["Single Image", "Carousel (5 Slides)", "Short-form Video Script"])
    context = st.text_area("Paste competitor URL or Ad copy to emulate:")
    prod_name = st.text_input("Your Product Name:")
    
    if st.button("Generate Ad Package", type="primary"):
        if ai_key:
            genai.configure(api_key=ai_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"Act as an expert Meta Ads Strategist. Create a high-converting {ad_type} for '{prod_name}'. Input context: {context}. Include Headlines, Primary Text, and detailed Visual Descriptions for designers."
            res = model.generate_content(prompt)
            st.markdown("### 🔥 Generated Ad Strategy")
            st.write(res.text)
        else: st.warning("Please enter your Gemini API Key in the sidebar.")

# --- 7. FEATURE: STORE SETTINGS ---
elif selected == "Store Settings":
    st.header("⚙️ Automation Brain: Cost Settings")
    st.write("Define your average fixed costs per unit. These are subtracted automatically in the Financial Oracle.")
    st.session_state.ship_cost = st.number_input("Average Shipping/Unit (₹)", value=st.session_state.ship_cost)
    st.session_state.ad_cost = st.number_input("Average Ad Spend/Unit (₹)", value=st.session_state.ad_cost)
    st.session_state.pkg_cost = st.number_input("Packaging & Fees/Unit (₹)", value=st.session_state.pkg_cost)
    st.success("Global store costs updated for this session.")

# --- 8. OWNER DASHBOARD (ADMIN PANEL) ---
elif selected == "Owner Dashboard":
    st.header("📈 Admin Revenue Ledger")
    try:
        res = supabase.table("user_tracking").select("*").execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            st.metric("Total Global 10% Share Due", f"₹{df['commission'].sum():,.2f}")
            st.dataframe(df, use_container_width=True)
        else: st.info("No profit data has been synced yet.")
    except Exception as e: st.error(f"Admin Error: {str(e)}")
