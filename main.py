import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# ==========================================
# 1. قاموس محرك البحث والترجمة الفورية للأسواق
# ==========================================
COMPANY_DICTIONARY = {
    "الراجحي": "1120.SR", "مصرف الراجحي": "1120.SR", "1120": "1120.SR",
    "أرامكو": "2222.SR", "أرامكو السعودية": "2222.SR", "ارامكو": "2222.SR", "2222": "2222.SR",
    "الأهلي": "1180.SR", "البنك الأهلي": "1180.SR", "1180": "1180.SR",
    "سابك": "2010.SR", "2010": "2010.SR",
    "الاتصالات السعودية": "7010.SR", "stc": "7010.SR", "7010": "7010.SR",
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
# 2. محرك الحسابات الفنية ومؤشر RSI
# ==========================================
def calculate_rsi(df, periods=14):
    if len(df) < periods:
        return pd.Series(50, index=df.index)
    close_delta = df['Close'].diff()
    up = close_delta.clip(lower=0)
    down = -1 * close_delta.clip(upper=0)
    ma_up = up.ewm(com=periods - 1, adjust=False).mean()
    ma_down = down.ewm(com=periods - 1, adjust=False).mean()
    rsi = ma_up / ma_down
    rsi = 100 - (100 / (1 + rsi))
    return rsi

def calculate_lightspeed_levels(current_price, high, low, rsi_value):
    range_movement = (high - low) if (high - low) > 0 else (current_price * 0.02)
    adjustment = 0.02 if rsi_value < 35 else (0.08 if rsi_value > 65 else 0.04)
    return {
        "entry": current_price - (range_movement * adjustment),
        "t1": current_price + (range_movement * 0.25),
        "t2": current_price + (range_movement * 0.55),
        "t3": current_price + (range_movement * 0.90),
        "sl": current_price - (range_movement * 0.15),
        "strict_sl": current_price - (range_movement * 0.30)
    }

# ==========================================
# 3. بناء واجهة مستخدم المنصة الرئيسية والمحاكي
# ==========================================
def main():
    st.title("📊 Lightspeed AI Radar pro")
    st.subheader("منصة التحليل والمحاكاة اللحظية لجميع الجلسات")
    
    if "trade_active" not in st.session_state:
        st.session_state.trade_active = False
    if "buy_price" not in st.session_state:
        st.session_state.buy_price = 0.0
    if "shares_count" not in st.session_state:
        st.session_state.shares_count = 0
    if "pnl_history" not in st.session_state:
        st.session_state.pnl_history = []

    st.sidebar.header("⚙️ إعدادات المنصة والربط")
    market_choice = st.sidebar.selectbox("اختر Market المستهدف:", ["السوق الأمريكي 🇺🇸", "السوق السعودي (تداول) 🇸🇦"])
    user_search = st.sidebar.text_input("أدخل اسم الشركة أو الرمز المباشر:", value="TSLA")
    timeframe = st.sidebar.selectbox("اختر الفريم الزمني للتحليل (Timeframe):", ["1m", "5m", "15m", "1h", "1d", "1wk"])
    trigger_radar = st.sidebar.button("تشغيل خوارزمية الرادار اللحظية", use_container_width=True)

    st.sidebar.markdown("---")
    st.sidebar.subheader("🔥 أسهم الترند والزخم اللحظي")
    if market_choice == "السوق السعودي (تداول) 🇸🇦":
        st.sidebar.code("1. الراجحي (1120)\n2. أرامكو (2222)\n3. سابك (2010)")
    else:
        st.sidebar.code("1. إنفيديا (NVDA)\n2. تسلا (TSLA)\n3. أبل (AAPL)")

    if trigger_radar or st.session_state.trade_active:
        ticker_resolved = resolve_ticker(user_search, market_choice)
        currency = "ر.س" if market_choice == "السوق السعودي (تداول) 🇸🇦" else "$"
        period_map = {"1m": "1d", "5m": "5d", "15m": "5d", "1h": "1mo", "1d": "6mo", "1wk": "2y"}
        
        hist = pd.DataFrame()
        try:
            ticker_obj = yf.Ticker(ticker_resolved)
            hist = ticker_obj.history(interval=timeframe, period=period_map[timeframe], prepost=True, auto_adjust=False, actions=False)
        except Exception as e:
            st.error(f"حدث خطأ أثناء الاتصال بالبورصة: {str(e)}")
            return

        if hist.empty:
            st.error("⚠️ تعذر جلب بيانات حية لهذه الجلسة، يرجى إعادة المحاولة.")
            return
            
        hist = hist.dropna(subset=['Close'])
        hist['RSI'] = calculate_rsi(hist)
        current_rsi = hist['RSI'].iloc[-1] if not hist['RSI'].empty else 50.0
        
        current_price = hist['Close'].iloc[-1]
        prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
        price_change = ((current_price - prev_price) / prev_price) * 100
        levels = calculate_lightspeed_levels(current_price, hist['High'].max(), hist['Low'].min(), current_rsi)

        st.subheader("📌 لوحة الفحص والمؤشرات اللحظية الدقيقة")
        st.markdown(f"### 🏢 الشركة النشطة: {ticker_resolved} | فريم التحليل: `{timeframe}`")
        
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric(label=f"السعر الفعلي اللحظي الآن ({currency})", value=f"{current_price:.2f}", delta=f"{price_change:.2f}%")
        with col_m2:
            st.metric(label="مؤشر القوة النسبية RSI للجلسة", value=f"{current_rsi:.2f}")
        with col_m3:
            last_vol = hist['Volume'].iloc[-1]
            liquidity_value = last_vol * current_price
            st.metric("سيولة الشمعة الحالية", f"{liquidity_value:,.0f} {currency}")
        
        st.markdown("---")

        st.subheader("📡 لوحة التداول التجريبي الحية (Paper Trading Mode)")
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            trade_shares = st.number_input("تحديد كمية الأسهم للصفقة:", min_value=1, max_value=10000, value=100)
        with col_btn2:
            if st.button("🛒 تنفيذ أمر BUY / شراء ماركت", use_container_width=True, disabled=st.session_state.trade_active):
                st.session_state.trade_active = True
                st.session_state.buy_price = current_price
                st.session_state.shares_count = trade_shares
                st.success(f"🚀 نجح الشراء! دخلت صفقة وهمية على الرمز {ticker_resolved} بكمية {trade_shares} سهم بسعر: {current_price:.2f} {currency}")
        with col_btn3:
            if st.button("⚡ تنفيذ أمر SELL / بيع وإغلاق", use_container_width=True, disabled=not st.session_state.trade_active):
                exit_price = current_price
                net_pnl = (exit_price - st.session_state.buy_price) * st.session_state.shares_count
                st.session_state.pnl_history.append(net_pnl)
                st.session_state.trade_active = False
                st.success(f"🏁 تمت تصفية الصفقة بسلام! سعر الخروج: {exit_price:.2f} {currency} | صافي ربح/خسارة العملية: {net_pnl:.2f} {currency}")

        if st.session_state.trade_active:
            current_pnl = (current_price - st.session_state.buy_price) * st.session_state.shares_count
            pnl_color = "green" if current_pnl >= 0 else "red"
            st.info(f"📋 **المركز المفتوح حالياً:** السعر المعلق: **{st.session_state.buy_price:.2f}** | الكمية: **{st.session_state.shares_count} سهم** | الأرباح اللحظية المتحركة الآن: <span style='color:{pnl_color}; font-weight:bold;'>{current_pnl:.2f} {currency}</span>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.subheader("🎯 مستويات القناص والأهداف الدقيقة المحتسب")
            st.success(f"🟢 منطقة أفضل دخول آمن للجلسة: **{levels['entry']:.2f} {currency}**")
            st.info(f"🚀 المستهدف المضاربي الأول: **{levels['t1']:.2f} {currency}**")
            st.info(f"🚀 المستهدف الفني الثاني: **{levels['t2']:.2f} {currency}**")
            st.info(f"🚀 المستهدف الرئيسي الثالث: **{levels['t3']:.2f} {currency}**")
            st.warning(f"⚠️ مستوى وقف الخسارة لحماية الأرباح: **{levels['sl']:.2f} {currency}**")
            st.error(f"🚨 وقف الخسارة الصارم النهائي: **{levels['strict_sl']:.2f} {currency}**")
        
        with col_t2:
            st.subheader("🔔 مركز الإشعارات الفورية ونصائح الرادار")
            if current_rsi >= 70:
                st.error("🔥 إشعار تضخم فني (Overbought): مؤشر RSI أعلى من 70! السهم في منطقة تشبع شرائي حاد ومخاطرة الدخول عالية جداً حالياً، انتظر التهدئة.")
            elif current_rsi <= 30:
                st.success("💎 إشعار اقتناص قاع (Oversold): مؤشر RSI تحت 30! السهم في منطقة تشبع بيعي مفرط فريدة، ويمثل فرصة تجميع ذهبية لارتداد سعري قوي قادم.")
            else:
                st.warning("⚖️ نصيحة الرادار: مؤشر RSI في نطاق متزن طبيعي (بين 30 و 70). المسار مناسب جداً للمضاربات السريعة واقتناص الفروقات السعرية في الجلسة الممتدة.")
        
        st.markdown("---")
        
        # بناء شارت الشموع المتكامل الموحد والخفيف جداً على السيرفر
        st.subheader(f"📈 شارت التحليل الفني لجميع جلسات التداول لفريم ({timeframe})")
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'], name="الشموع"))
        fig.add_hline(y=levels['entry'], line_dash="dash", line_color="green", annotation_text="منطقة الدخول")
        fig.add_hline(y=levels['t1'], line_dash="dash", line_color="blue", annotation_text="الهدف 1")
        fig.add_hline(y=levels['sl'], line_dash="dash", line_color="red", annotation_text="وقف الخسارة")
        fig.update_layout(xaxis_rangeslider_visible=False, height=480, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
