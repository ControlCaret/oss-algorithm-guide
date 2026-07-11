import streamlit as st
import requests
import os

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

current_dir = os.path.dirname(os.path.abspath(__file__))
css_path = os.path.join(current_dir, "css", "style.css")

@st.cache_data
def load_css(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f"<style>{f.read()}</style>"
    return ""

st.set_page_config(
    page_title="알고리즘 문제 추천기",
    page_icon="🎯",
    layout="centered"
)

st.markdown(load_css(css_path), unsafe_allow_html=True)

st.title("알고리즘 문제 추천기")
st.write("사용자의 성향과 역량 수준에 따른 알고리즘 문제를 추천합니다.")

with st.form("user_profile_form"):
    st.write("### 사용자 성향 조사")
    
    languages = st.multiselect(
        "사용 프로그래밍 언어 (다중 선택 가능)",
        options=[
            "Python3", "C++", "Java", "Python", "C", "C#", 
            "JavaScript", "TypeScript", "Go", "Rust", 
            "Kotlin", "Swift", "Scala", "Ruby", "PHP", 
            "Dart", "Racket", "Erlang", "Elixir",
            "MySQL", "MS SQL Server", "Oracle", "PostgreSQL"
        ],
        default=["Python3", "C++"]
    )
    
    st.write("")
    st.write("#### 분야별 선호도 및 수준")
    
    tags = [
        ("Math", "수학"),
        ("Implementation", "구현"),
        ("Dynamic Programming", "동적 계획법"),
        ("Data Structure", "자료 구조"),
        ("Graph", "그래프"),
        ("Sorting", "정렬")
    ]
    tag_assessments = {}
    
    col_left, col_right = st.columns(2)
    left_tags = tags[:3]
    right_tags = tags[3:]
    
    def render_tag_card(tag_pair):
        eng, kr = tag_pair
        with st.container(border=True):
            st.markdown(f"**{eng}** <span class='tag-subtitle'>({kr})</span>", unsafe_allow_html=True)
            
            skill_res = st.pills(
                "수준",
                options=["입문", "숙련", "전문"],
                selection_mode="single",
                default="숙련",
                key=f"{eng}_skill_pills"
            )
            skill_str = skill_res if skill_res is not None else "숙련"
            
            pref_res = st.pills(
                "선호도",
                options=["기피", "보통", "선호"],
                selection_mode="single",
                default="보통",
                key=f"{eng}_pref_pills"
            )
            pref_str = pref_res if pref_res is not None else "보통"
            
            pref_val = 1 if pref_str == "선호" else -1 if pref_str == "기피" else 0
            skill_val = 1 if skill_str == "전문" else -1 if skill_str == "입문" else 0
            
            return {
                "preference": pref_val,
                "skill": skill_val
            }

    with col_left:
        for tag_pair in left_tags:
            tag_assessments[tag_pair[0].lower()] = render_tag_card(tag_pair)
            
    with col_right:
        for tag_pair in right_tags:
            tag_assessments[tag_pair[0].lower()] = render_tag_card(tag_pair)
        
    submitted = st.form_submit_button("추천 문제 분석 시작", type="primary", use_container_width=True)

if submitted:
    if not languages:
        st.error("최소 하나의 언어를 선택해 주세요.")
    else:
        recommend_payload = {
            "languages": [lang.lower() for lang in languages],
            "tag_assessments": tag_assessments
        }
        
        try:
            with st.spinner("추천 문제를 선정하고 있습니다..."):
                res_rec = requests.post(f"{BACKEND_URL}/recommend", json=recommend_payload)
            if res_rec.status_code == 200:
                recommended_problems = res_rec.json().get("recommended_problems", [])
                if recommended_problems:
                    problem = recommended_problems[0]
                    
                    st.success("추천 문제를 선정했습니다.")
                    
                    with st.container(border=True):
                        st.markdown(f"### {problem['title']}")
                        st.markdown(f"**난이도:** {problem['difficulty']}")
                        st.write("**관련 태그:**")
                        clean_tags = [t.replace("'", "").strip() for t in problem['tags']]
                        st.pills(
                            "tags_view",
                            options=clean_tags,
                            selection_mode="single",
                            label_visibility="collapsed",
                            key=f"tags_pills_{problem['id']}"
                        )
                        st.write("")
                        st.link_button("LeetCode에서 문제 해결하기", problem['url'], use_container_width=True)
                    
                    with st.spinner("AI 멘토가 맞춤 가이드를 구성하고 있습니다..."):
                        feedback_payload = {
                            "recommended_problems": recommended_problems,
                            "tag_assessments": tag_assessments
                        }
                        res_feed = requests.post(f"{BACKEND_URL}/recommend/feedback", json=feedback_payload)
                        
                        if res_feed.status_code == 200:
                            analyses = res_feed.json().get("analyses", [])
                            if analyses:
                                analysis = analyses[0]
                                st.write("### AI 멘토링 가이드")
                                with st.container(border=True):
                                    st.markdown(f"**문제 핵심 요약**\n\n{analysis['overview']}")
                                    st.markdown("---")
                                    st.markdown(f"**멘토의 추천 사유**\n\n{analysis['reason']}")
                                    st.markdown("---")
                                    st.markdown(f"**해결 핵심 힌트**\n\n{analysis['hint']}")
                            else:
                                st.warning("AI 분석 피드백 결과를 받아오지 못했습니다.")
                        else:
                            try:
                                err_data = res_feed.json()
                                err_detail = f"AI Error ({res_feed.status_code}): {err_data.get('detail', 'API Error')}"
                            except Exception:
                                err_detail = f"AI Error ({res_feed.status_code}): Connection failed"
                            st.error(err_detail)
                else:
                    st.warning("조건에 부합하는 추천 문제를 찾지 못했습니다.")
            else:
                st.error("추천 문제 로딩 중 백엔드 서버 오류가 발생했습니다.")
        except Exception as e:
            st.error(f"서버 연결 실패: {str(e)}")
