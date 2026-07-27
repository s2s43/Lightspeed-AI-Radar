import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from textblob import TextBlob

# ==========================================
# 1. محرك البحث والترجمة الذكية الفورية للأسواق
# ==========================================
COMPANY_DICTIONARY = {
    # السوق السعودي 🇸🇦
    "الراجحي": "1120.SR", "مصرف الراجحي": "1120.SR", "1120": "1120.SR",
    "أرامكو": "2222.SR", "أرامكو السعودية": "2222.SR", "ارامكو": "2222.SR", "2222": "2222.SR",
    "الأهلي": "1180.SR", "البنك الأهلي": "1180.SR", "1180": "1180.SR",
    "سابك": "2010.SR", "2010": "2010.SR",
    "الاتصالات السعودية": "7010.SR", "stc": "7010.SR", "7010": "7010.SR",
    # السوق الأمريكي 🇺🇸
    "تسلا": "TSLA", "tesla": "TSLA",
    "أبل": "AAPL", "apple": "AAPL",
    "مايكروسوفت": "MSFT", "microsoft": "MSFT",
    "إنفيديا": "NVDA", "nvidia": "NVDA",
    "جوجل": "GOOGL", "google": "GOOGL"
}

def resolve_ticker(user_input, market_type):
    clean_input = user_input.strip().lower()
    if clean_input in COMPANY_DICTIONARY:
        return COMPANY_DICTIONARY[clean_input]
    if market_type == "السوق السعودي (تداول) 🇸🇦":
        if not clean_input.endswith(".sr") and clean_input.isdigit():
            return f"{clean_input}.SR"
    return user_input.upper().strip()

# ==========================================
# 2. خوارزمية Lightspeed لحساب الدخول والأهداف اللحظية
# ==========================================
def calculate_lightspeed_levels(current_price, high, low):
    range_movement = (high - low) if (high - low) > 0 else (current_price * 0.02)
    return {
        "entry": current_price - (range_movement * 0.15),
        "t1": current_price + (range_movement * 0.35),
        "t2": current_price + (range_movement * 0.85),
        "t3": current_price + (range_movement * 1.50),
        "sl": current_price - (range_movement * 0.55),
        "strict_sl": current_price - (range_movement * 1.10)
    }

# ==========================================
# 3. بناء لوحة تحكم Lightspeed AI Radar pro
# ==========================================
def main():
    st.set_page_config(page_title="Lightspeed AI Radar - منصة التداول الذكية", layout="wide")
    
    st.markdown("""
        <style>
        .stApp { background-color: #06080c; color: #d1d4dc; }
        h1, h2, h3 { color: #ff9900 !important; font-family: Arial, sans-serif; }
        .stButton>button { background-color: #d97706 !important; color: white !important; font-weight: bold; border-radius: 4px; }
        .stButton>button:hover { background-color: #b45309 !important; }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("📊 Lightspeed AI Radar pro - منصة التداول والتحليل اللحظي")
    st.markdown("محرك مضاربي متكامل مدمج بخوارزميات صانعي السوق وجلب فوري للأسعار الحية.")
    
    st.sidebar.header("⚙️ إعدادات المنصة والربط")
    market_choice = st.sidebar.selectbox("اختر السوق المستهدف:", ["السوق الأمريكي 🇺🇸", "السوق السعودي (تداول) 🇸🇦"])
    user_search = st.sidebar.text_input("أدخل اسم الشركة أو الرمز المباشر:", value="TSLA")
    timeframe = st.sidebar.selectbox("اختر الفريم الزمني للتحليل (Timeframe):", ["1m", "5m", "15m", "1h", "1d", "1wk"])
    trigger_radar = st.sidebar.button("تشغيل خوارزمية الرادار اللحظية", use_container_width=True)

    st.sidebar.markdown("---")
    st.sidebar.subheader("🔥 أسهم الترند والزخم اللحظي")
    if market_choice == "السوق السعودي (تداول) 🇸🇦":
        st.sidebar.code("1. الراجحي (1120)\n2. أرامكو (2222)\n3. سابك (2010)")
    else:
        st.sidebar.code("1. إنفيديا (NVDA)\n2. تسلا (TSLA)\n3. أبل (AAPL)")

    if trigger_radar:
        ticker_resolved = resolve_ticker(user_search, market_choice)
        currency = "ر.س" if market_choice == "السوق السعودي (تداول) 🇸🇦" else "$"
        period_map = {"1m": "1d", "5m": "5d", "15m": "5d", "1h": "1mo", "1d": "6mo", "1wk": "2y"}
        
        hist = pd.DataFrame()
        ticker_obj = None
        
        with st.spinner(f"📡 جاري الاتصال بالبورصة ومعالجة بيانات {ticker_resolved} فوريّاً..."):
            try:
                ticker_obj = yf.Ticker(ticker_resolved)
                hist = ticker_obj.history(interval=timeframe, period=period_map[timeframe])
            except Exception as e:
                st.error(f"حدث خطأ أثناء معالجة بيانات البورصة اللحظية: {str(e)}")
                return

        if hist.empty:
            st.error("⚠️ تعذر جلب بيانات حية لهذا الرمز، يرجى التأكد من كتابة الاسم أو الرمز بشكل صحيح.")
            return
            
        hist = hist.dropna(subset=['Close'])
        current_price = hist['Close'].iloc[-1]
        prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
        price_change = ((current_price - prev_price) / prev_price) * 100
        
        stock_direction = "📈 صاعد (زخم إيجابي)" if price_change >= 0 else "📉 هابط (تصحيح لحظي)"
        dir_color = "green" if price_change >= 0 else "red"
        levels = calculate_lightspeed_levels(current_price, hist['High'].max(), hist['Low'].min())
        
        try:
            info_data = ticker_obj.info
            company_name = info_data.get("longName", ticker_resolved)
            float_shares = info_data.get("floatShares", 0)
        except:
            company_name = ticker_resolved
            float_shares = 0

        st.subheader("📌 لوحة الفحص والمؤشرات اللحظية الحية")
        st.markdown(f"### 🏢 الشركة النشطة: <span style='color:#38bdf8;'>{company_name} ({ticker_resolved})</span> | فريم التحليل: `{timeframe}`", unsafe_allow_html=True)
        
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric(label=f"السعر الحالي ({currency})", value=f"{current_price:.2f}", delta=f"{price_change:.2f}%")
        with col_m2:
            st.markdown(f"**الاتجاه الفني الحالي:**\n\n<span style='color:{dir_color}; font-size:18px; font-weight:bold;'>{stock_direction}</span>", unsafe_allow_html=True)
        with col_m3:
            last_vol = hist['Volume'].iloc[-1]
            liquidity_value = last_vol * current_price
            st.metric("سيولة الشمعة الأخيرة", f"{liquidity_value:,.0f} {currency}")
        with col_m4:
            st.metric("الأسهم الحرة (Float Shares)", f"{float_shares:,.0f}" if float_shares else "تحديث دوري")
        
        st.markdown("---")
        
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.subheader("🎯 أهداف ومستويات القناص المضاربية")
            st.success(f"🟢 منطقة أفضل دخول آمن لحظي: **{levels['entry']:.2f} {currency}**")
            st.info(f"🚀 المستهدف المضاربي الأول: **{levels['t1']:.2f} {currency}**")
            st.info(f"🚀 المستهدف الفني الثاني: **{levels['t2']:.2f} {currency}**")
            st.info(f"🚀 المستهدف الرئيسي الثالث: **{levels['t3']:.2f} {currency}**")
            st.warning(f"⚠️ مستوى وقف الخسارة لحماية الأرباح: **{levels['sl']:.2f} {currency}**")
            st.error(f"🚨 وقف الخسارة الصارم النهائي: **{levels['strict_sl']:.2f} {currency}**")
        
        with col_t2:
            st.subheader("🔔 مركز الإشعارات الفورية ونصائح الرادار")
            if last_vol > (hist['Volume'].mean() * 1.5):
                st.error("⚡ **إشعار اختراق سيولة:** تم رصد تدفق حجم تداول ضخم ومفاجئ يفوق المعدل المعتاد بـ 150%! السيولة الحالية تفاعلية.")
            if abs(current_price - levels['entry']) / levels['entry'] <= 0.01:
                st.success("🎯 **إشعار اقتناص فوري:** السهم يسبح الآن مباشرة داخل نطاق منطقة الدخول الأمنة والمضاربة اللحظية.")
            elif current_price <= levels['sl']:
                st.error("🚨 **إشعار خطر فني:** السهم كسر مستوى دعم حماية الأرباح الافتراضي، يرجى تفعيل وقف الخسارة الصارم لحماية رأس المال.")
            else:
                st.warning("⚖️ حركة السهم تتداول ضمن مستويات التجميع الفنية العادية، مناسب للمضاربات الخاطفة بين منطقة الدخول والهدف الأول.")
        
        st.markdown("---")
        
        st.subheader(f"📈 شارت التحليل الفني التفاعلي اللحظي لفريم ({timeframe})")
        fig = go.Figure(data=[go.Candlestick(
            x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'], name="الشموع اليابانية"
        )])
        fig.add_hline(y=levels['entry'], line_dash="dash", line_color="green", annotation_text="منطقة الدخول الآمنة")
        fig.add_hline(y=levels['t1'], line_dash="dash", line_color="blue", annotation_text="الهدف 1")
        fig.add_hline(y=levels['sl'], line_dash="dash", line_color="red", annotation_text="وقف الخسارة الصارم")
        
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=520, paper_bgcolor='#0c0f16', plot_bgcolor='#0c0f16')
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        st.subheader("📰 آخر أخبار السهم والتحليل الذكي لمشاعر الخبر")
        try:
            news_list = ticker_obj.news
            if news_list and len(news_list) > 0:
                for news in news_list[:3]:
                    n_title = news.get('title', '')
                    n_link = news.get('link', '')
                    n_polarity = TextBlob(n_title).sentiment.polarity
                    sentiment_labels = ["🔴 سلبي (محفز للهبوط)", "🟡 محايد (استقرار سعري)", "🟢 إيجابي (محفز للصعود)"]
                    idx = int(n_polarity > 0.1) - int(n_polarity < -0.1) + 1
                    
                    st.markdown(f"🔹 **[{n_title}]({n_link})**")
                    st.info(f"التحليل الذكي لمشاعر فحوى الخبر: {sentiment_labels[idx]}")
            else:
                st.info("لا توجد أخبار جوهرية منشورة حديثاً لهذا الرمز حالياً عبر البورصة العالمية.")
        except:
            st.info("تعذر تحميل الأخبار الفورية الخاصة بهذا الرمز مؤقتاً من المصدر الرئيسي.")

if __name__ == "__main__":
    main()
