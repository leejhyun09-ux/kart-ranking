import json
import os
import streamlit as st

DATA_FILE = "kart_records.json"
IMAGE_DIR = "uploaded_images"

if not os.path.exists(IMAGE_DIR):
  os.makedirs(IMAGE_DIR)

# 관리자 비밀번호 설정 (필요시 변경하세요)
ADMIN_PASSWORD = "1234"


def load_data():
  """저장된 기록 데이터를 불러옵니다."""
  if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
      return json.load(f)
  return {"빌리지 고가": [], "동화이솝우화": []}


def save_data(data):
  """기록 데이터를 파일에 저장합니다."""
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


data = load_data()

st.title("🏎️ 카트라이더 타임어택 랭킹 판")
st.write("친구들과 함께 기록과 인증샷을 등록하고 순위를 경쟁해보세요!")

menu = st.sidebar.selectbox(
    "메뉴 선택",
    ["전체 순위 보기", "기록 입력", "새 맵 추가", "기록 삭제 (본인/관리자)"],
)

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
          for i, rec in enumerate(records, 1):
            cols = st.columns([1, 3, 3, 4])
            cols[0].write(f"**{i}위**")
            cols[1].write(rec["player"])
            cols[2].write(rec["time"])

            if "image_path" in rec and rec["image_path"]:
              if os.path.exists(rec["image_path"]):
                cols[3].image(rec["image_path"], width=150)
              else:
                cols[3].write("사진을 찾을 수 없음")
            else:
              cols[3].write("인증샷 없음")
            st.divider()

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

      uploaded_file = st.file_uploader(
          "주행 인증샷 업로드 (선택)", type=["png", "jpg", "jpeg"]
      )

      submit_button = st.form_submit_button(label="기록 등록하기")

      if submit_button:
        if not player_name or not record_time:
          st.error("이름과 기록을 모두 입력해주세요.")
        else:
          image_path = None
          if uploaded_file is not None:
            image_filename = f"{selected_map}_{player_name}_{uploaded_file.name}"
            image_path = os.path.join(IMAGE_DIR, image_filename)
            with open(image_path, "wb") as f:
              f.write(uploaded_file.getbuffer())

          existing_record = None
          for rec in data[selected_map]:
            if rec["player"] == player_name:
              existing_record = rec
              break

          updated = False
          if existing_record:
            if record_time < existing_record["time"]:
              if (
                  "image_path" in existing_record
                  and existing_record["image_path"]
                  and os.path.exists(existing_record["image_path"])
              ):
                os.remove(existing_record["image_path"])

              data[selected_map].remove(existing_record)
              data[selected_map].append({
                  "player": player_name,
                  "time": record_time,
                  "image_path": image_path,
              })
              updated = True
              st.success(
                  f"🎉 신기록 달성! {player_name}님의 기록이"
                  f" {record_time}(으)로 갱신되었습니다!"
              )
            else:
              if image_path and os.path.exists(image_path):
                os.remove(image_path)
              st.warning(
                  f"❌ 기존 최고 기록({existing_record['time']})보다 느리거나"
                  " 같습니다. 갱신되지 않았습니다."
              )
          else:
            data[selected_map].append({
                "player": player_name,
                "time": record_time,
                "image_path": image_path,
            })
            updated = True
            st.success(
                f"✅ {player_name}님의 기록({record_time})이 등록되었습니다!"
            )

          if updated:
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

elif menu == "기록 삭제 (본인/관리자)":
  st.header("🗑️ 기록 삭제 센터")
  st.write(
      "원하는 삭제 방식을 선택하세요. (본인 이름으로 삭제 또는 관리자"
      " 비밀번호로 전체 삭제)"
  )

  # 삭제 방식 선택 탭
  delete_mode = st.radio(
      "삭제 방식 선택", ["내 기록 삭제 (일반)", "관리자 모드로 삭제"]
  )

  if not data:
    st.info("등록된 데이터가 없습니다.")
  else:
    if delete_mode == "내 기록 삭제 (일반)":
      with st.form("my_delete_form"):
        selected_map = st.selectbox(
            "삭제할 기록이 있는 맵 선택", list(data.keys()), key="my_map"
        )
        input_player_name = st.text_input(
            "본인 플레이어 이름 입력", key="my_name"
        ).strip()
        delete_submit = st.form_submit_button(label="내 기록 삭제하기")

        if delete_submit:
          if not input_player_name:
            st.error("플레이어 이름을 입력해주세요.")
          else:
            target_record = None
            for rec in data[selected_map]:
              if rec["player"] == input_player_name:
                target_record = rec
                break

            if target_record:
              if (
                  "image_path" in target_record
                  and target_record["image_path"]
                  and os.path.exists(target_record["image_path"])
              ):
                os.remove(target_record["image_path"])

              data[selected_map].remove(target_record)
              save_data(data)
              st.success(
                  f"🗑️ '{selected_map}' 맵에서 '{input_player_name}'님의 기록이"
                  " 삭제되었습니다!"
              )
              st.rerun()
            else:
              st.error(
                  f"'{selected_map}' 맵에 '{input_player_name}'님의 기록이"
                  " 존재하지 않습니다."
              )

    elif delete_mode == "관리자 모드로 삭제":
      password_input = st.text_input(
          "관리자 비밀번호 입력", type="password", key="admin_pw"
      )

      if password_input == ADMIN_PASSWORD:
        st.success("관리자 권한이 확인되었습니다.")

        with st.form("admin_delete_form"):
          selected_map = st.selectbox(
              "삭제할 기록이 있는 맵 선택", list(data.keys()), key="admin_map"
          )

          if not data[selected_map]:
            st.write("이 맵에는 등록된 기록이 없습니다.")
            admin_delete_submit = st.form_submit_button(
                label="기록 삭제", disabled=True
            )
          else:
            player_list = [rec["player"] for rec in data[selected_map]]
            selected_player = st.selectbox(
                "삭제할 플레이어 선택", player_list, key="admin_player"
            )
            admin_delete_submit = st.form_submit_button(
                label="선택한 기록 강제 삭제"
            )

          if admin_delete_submit and data[selected_map]:
            target_record = None
            for rec in data[selected_map]:
              if rec["player"] == selected_player:
                target_record = rec
                break

            if target_record:
              if (
                  "image_path" in target_record
                  and target_record["image_path"]
                  and os.path.exists(target_record["image_path"])
              ):
                os.remove(target_record["image_path"])

              data[selected_map].remove(target_record)
              save_data(data)
              st.success(
                  f"🗑️ [관리자] '{selected_map}' 맵에서 '{selected_player}'님의"
                  " 기록이 삭제되었습니다!"
              )
              st.rerun()

      elif password_input != "":
        st.error("비밀번호가 틀렸습니다.")
      else:
        st.info("관리자 권한으로 삭제하려면 비밀번호를 입력해주세요.")
