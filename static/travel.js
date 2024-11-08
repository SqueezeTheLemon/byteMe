
//여기서부터-->
let currentIndex = 0;

document.addEventListener("DOMContentLoaded", function () {
    const sliderContainer = document.querySelector('.image-container');
    const sliderImages = document.querySelectorAll('.image-slide');
    const orderCountElement = document.getElementById('order-count');
    const paginationDots = document.querySelectorAll('.dot');
    
    let orderCount = 9;  // 서버에서 주문횟수 받아야 하는데 일단 4로 함
    orderCountElement.textContent = `나의 주문횟수: ${orderCount}`;

    // 슬라이드 이동 함수
    function moveSlide(direction) {
        const totalSlides = sliderImages.length;

        currentIndex += direction;

        if (currentIndex < 0) {
            currentIndex = totalSlides - 1;
        } else if (currentIndex >= totalSlides) {
            currentIndex = 0;
        }

        sliderContainer.style.transform = `translateX(-${currentIndex * 100}%)`;
        updatePagination();
    }

    // 페이지네이션 업데이트 함수
    function updatePagination() {
        paginationDots.forEach((dot, index) => {
            if (index === currentIndex) {
                dot.style.backgroundColor = '#717171';
            } else {
                dot.style.backgroundColor = '#bbb';
            }
        });
    }

    // 주문횟수에 따라 이미지 변경 함수
    function checkOrderCountAndUpdateImage(count) {
        if (count >= 4 && count < 8) {
            sliderImages[0].querySelector('img').src = "trv1.png";
          } else if (count >= 8 && count < 12) {
            sliderImages[0].querySelector('img').src = "trv1.png";
            sliderImages[1].querySelector('img').src = "trv2-2.png";
          } else if (count >= 12 && count < 16) {
            sliderImages[0].querySelector('img').src = "trv1.png";
            sliderImages[1].querySelector('img').src = "trv2-3.png";
          } else if (count >= 16 && count < 20) {
            sliderImages[0].querySelector('img').src = "trv1.png";
            sliderImages[1].querySelector('img').src = "trv2.png";
            sliderImages[2].querySelector('img').src = "trv3-1.png";
          } else if (count >= 20 && count < 24) {
            sliderImages[0].querySelector('img').src = "trv1.png";
            sliderImages[1].querySelector('img').src = "trv2.png";
            sliderImages[2].querySelector('img').src = "trv3-2.png"; 
          } else if (count >=24 ){
            sliderImages[0].querySelector('img').src = "trv1.png";
            sliderImages[1].querySelector('img').src = "trv2.png";
            sliderImages[2].querySelector('img').src = "trv3.png";
          }
    }

    
    // // 주문횟수 증가 후 이미지 변경 = = = 테스트 코드
    // setInterval(() => {
    //     orderCount += 1;
    //     orderCountElement.textContent = `나의 주문횟수: ${orderCount}`;
    //     checkOrderCountAndUpdateImage(orderCount);  // 주문횟수에 맞춰 이미지 변경

    //     // 이미지 변경 후에도 슬라이드가 올바르게 동작하도록 유지
    //     sliderContainer.style.transform = `translateX(-${currentIndex * 100}%)`;
    // }, 5000); //테스트: 5초마다 주문횟수를 증가시킴

    // 슬라이드 이동 버튼 클릭 이벤트
    document.querySelector('.prev').addEventListener('click', () => moveSlide(-1));
    document.querySelector('.next').addEventListener('click', () => moveSlide(1));
    
    // 페이지네이션 클릭 이벤트
    paginationDots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            currentIndex = index;
            sliderContainer.style.transform = `translateX(-${currentIndex * 100}%)`;
            updatePagination();
            updateDescription(currentIndex);
        });
    });

    // 초기 상태 업데이트
    updatePagination();
});


