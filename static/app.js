// Select The Elements
var toggle_btn;
var big_wrapper;
var hamburger_menu;

function declare() {
  toggle_btn = document.querySelector(".toggle-btn");
  big_wrapper = document.querySelector(".big-wrapper");
  hamburger_menu = document.querySelector(".hamburger-menu");
}

const main = document.querySelector("main");

declare();

let dark = false;

function toggleAnimation() {
  // Clone the wrapper
  dark = !dark;
  let clone = big_wrapper.cloneNode(true);
  if (dark) {
    clone.classList.remove("light");
    clone.classList.add("dark");
  } else {
    clone.classList.remove("dark");
    clone.classList.add("light");
  }
  clone.classList.add("copy");
  main.appendChild(clone);

  document.body.classList.add("stop-scrolling");

  clone.addEventListener("animationend", () => {
    document.body.classList.remove("stop-scrolling");
    big_wrapper.remove();
    clone.classList.remove("copy");
    // Reset Variables
    declare();
    events();
  });
}

function events() {
  toggle_btn.addEventListener("click", toggleAnimation);
  hamburger_menu.addEventListener("click", () => {
    big_wrapper.classList.toggle("active");
  });
}

events();

const sliderItems = document.querySelectorAll('.how-to-play .slider-item');
const controls = document.querySelectorAll('.how-to-play .slider-controls .control');
let currentSlide = 0;

// Auto-slide function
function autoSlide() {
  const prevSlide = currentSlide;
  currentSlide = (currentSlide + 1) % sliderItems.length;
  sliderItems[prevSlide].classList.remove('active');
  sliderItems[currentSlide].classList.add('active');
  controls[prevSlide].classList.remove('active');
  controls[currentSlide].classList.add('active');
}

// Slider controls
controls.forEach((control, index) => {
  control.addEventListener('click', () => {
    sliderItems[currentSlide].classList.remove('active');
    controls[currentSlide].classList.remove('active');
    currentSlide = index;
    sliderItems[currentSlide].classList.add('active');
    controls[currentSlide].classList.add('active');
  });
});

// Auto-slide interval
setInterval(autoSlide, 5000);


