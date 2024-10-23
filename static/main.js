// 등록 버튼 클릭 시 팝업
function click_submit(){
    alert("등록되었습니다!");
}

// 리스너 등록
const submit = document.getElementById("submit");
submit.addEventListener("click", click_submit);