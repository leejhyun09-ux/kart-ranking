import json
import os
import streamlit as st

DATA_FILE = "kart_records.json"


def load_data():
  """저장된 기록 데이터를 불러옵니다."""
  if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
      return json.load(f)
  return {
      "빌리지 고가": [],
      "동화이솝우화": [],
  }  # 기본 맵 예시


def save_data(data):
  """기록 데이터를 파일에 저장합니다."""
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


# 데이터 불러오기
data = load_data()

st.title("🏎️ 카트라이더 타임어택 랭킹 판")
st.write("친구들과 함께 기록을 등록하고 순위를 경쟁해보세요!")

# 사이드바 메뉴
menu = st.sidebar.selectbox("메뉴 선택", ["전체 순위 보기", "기록 입력", "새 맵 추가"])

if menu == "전체 순위 보기":
  st.header("🏆 맵별 최고 순위")

  if not data:
    st.info("등록된 맵이 없습니다.")
  else:
    for map_name, records in data.items():
      with st.expander(f"📍 {map_name}", expanded=True):
        if not records:
          st.write("아직 등록된 기록이 없습니다.")
        else:
          # 표 형태로 깔끔하게 출력하기 위해 데이터 가공
          rank_data = []
          for i, rec in enumerate(records, 1):
            rank_data.append(
                {"순위": f"{i}위", "플레이어": rec["player"], "기록": rec["time"]}
            )
          st.table(rank_data)

elif menu == "기록 입력":
  st.header("⏱️ 새 기록 등록")

  if not data:
    st.warning("먼저 '새 맵 추가' 메뉴에서 맵을 추가해주세요.")
  else:
    with st.form("record_form"):
      selected_map = st.selectbox("맵 선택", list(data.keys()))
      player_name = st.text_input("플레이어 이름").strip()
      record_time = st.text_input(
          "기록 (예: 01:23.45 형식으로 입력)"
      ).strip()

      submit_button = st.form_submit_button(label="기록 등록하기")

      if submit_button:
        if not player_name or not record_time:
          st.error("이름과 기록을 모두 입력해주세요.")
        else:
          # 기존 플레이어 기록 확인
          existing_record = None
          for rec in data[selected_map]:
            if rec["player"] == player_name:
              existing_record = rec
              break

          updated = False
          if existing_record:
            # 기존 기록보다 더 빠를 때만 갱신
            if record_time < existing_record["time"]:
              data[selected_map].remove(existing_record)
              data[selected_map].append(
                  {"player": player_name, "time": record_time}
              )
              updated = True
              st.success(
                  f"🎉 신기록 달성! {player_name}님의 기록이"
                  f" {record_time}(으)로 갱신되었습니다!"
              )
            else:
              st.warning(
                  f"❌ 기존 최고 기록({existing_record['time']})보다 느리거나"
                  " 같습니다. 갱신되지 않았습니다."
              )
          else:
            data[selected_map].append(
                {"player": player_name, "time": record_time}
            )
            updated = True
            st.success(
                f"✅ {player_name}님의 기록({record_time})이 등록되었습니다!"
            )

          if updated:
            # 빠른 시간순 정렬
            data[selected_map].sort(key=lambda x: x["time"])
            save_data(data)

elif menu == "새 맵 추가":
  st.header("🗺️ 새로운 맵 추가")

  with st.form("map_form"):
    new_map_name = st.text_input("추가할 맵 이름").strip()
    map_submit = st.form_submit_button(label="맵 추가하기")

    if map_submit:
      if not new_map_name:
        st.error("맵 이름을 입력해주세요.")
      elif new_map_name in data:
        st.warning("이미 존재하는 맵입니다.")
      else:
        data[new_map_name] = []
        save_data(data)
        st.success(f"🏁 '{new_map_name}' 맵이 성공적으로 추가되었습니다!")