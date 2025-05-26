(function ($) {
	"use strict";

	// Preloader 
	jQuery(window).on('load', function () {
		$(".preloader").delay(1600).fadeOut("slow");
	});

	$('.sidebar-button').on("click", function () {
		$(this).toggleClass('active');
	});

	document.querySelector('.sidebar-button').addEventListener('click', () =>
		document.querySelector('.main-menu').classList.toggle('show-menu'));

	$('.menu-close-btn').on("click", function () {
		$('.main-menu').removeClass('show-menu');
	});


	// Sidebar 
	$('.sidebar-btn').on("click", function () {
		$('.sidebar-area').addClass('active');
	});
	$('.sidebar-menu-close').on("click", function () {
		$('.sidebar-area').removeClass('active');
	});

	jQuery('.dropdown-icon').on('click', function () {
		jQuery(this).toggleClass('active').next('ul').slideToggle();
		jQuery(this).parent().siblings().children('ul').slideUp();
		jQuery(this).parent().siblings().children('.active').removeClass('active');
	});
	jQuery('.dropdown-icon2').on('click', function () {
		jQuery(this).toggleClass('active').next('.submenu-list').slideToggle();
		jQuery(this).parent().siblings().children('.submenu-list').slideUp();
		jQuery(this).parent().siblings().children('.active').removeClass('active');
	});


	document.addEventListener("DOMContentLoaded", function () {
		// Function to apply the 'left' style to '.onsale' elements
		function applyOnsaleStyle() {
			var onsaleElements = document.querySelectorAll('.onsale');
			onsaleElements.forEach(function (onsaleElement) {
				onsaleElement.style.left = '130px';
			});
		}

		// Check if the 'flex-viewport' class is present on page load
		if (document.querySelector('.flex-viewport')) {
			applyOnsaleStyle();
		} else {
			// Use MutationObserver to detect when the 'flex-viewport' class is added
			var observer = new MutationObserver(function (mutationsList, observer) {
				mutationsList.forEach(function (mutation) {
					mutation.addedNodes.forEach(function (addedNode) {
						if (addedNode.nodeType === 1 && addedNode.classList.contains('flex-viewport')) {
							applyOnsaleStyle();
							observer.disconnect(); // Stop observing after the class is found
						}
					});
				});
			});

			// Observe changes in the document body
			observer.observe(document.body, {
				childList: true,
				subtree: true
			});
		}
	});


	//Counter up
	if (document.querySelector('.counter')) {
		$('.counter').counterUp({
			delay: 10,
			time: 1500
		});
	}
	// Video Popup

	$('[data-fancybox="gallery"]').fancybox({
		buttons: [
			"close"
		],
		loop: false,
		protect: true
	});
	$('.video-player').fancybox({
		buttons: [
			"close"
		],
		loop: false,
		protect: true
	});

	// niceSelect
	$('select:not(.country_select,.state_select,.product_tag_search,.country_to_state,.wc-enhanced-select)').niceSelect();


	// testimonial Slider
	var swiper = new Swiper(".testimonial-slider", {
		slidesPerView: 1,
		speed: 1500,
		spaceBetween: 25,
		pauseOnMouseEnter: true,
		autoplay: {
			delay: 2500,
			disableOnInteraction: false,
		},
		navigation: {
			nextEl: ".next-1",
			prevEl: ".prev-1",
		},

		breakpoints: {
			280: {
				slidesPerView: 1,
			},
			386: {
				slidesPerView: 1,
			},
			576: {
				slidesPerView: 1,
			},
			768: {
				slidesPerView: 2,
			},
			992: {
				slidesPerView: 2,
			},
			1200: {
				slidesPerView: 3,
			},
			1400: {
				slidesPerView: 3,
			},
		},
	});
	// Home1 auction Slider
	var swiper = new Swiper(".auction-slider", {
		slidesPerView: 1,
		speed: 1500,
		spaceBetween: 25,
		pauseOnMouseEnter: true,
		autoplay: {
			delay: 2500,
			disableOnInteraction: false,
		},
		navigation: {
			nextEl: ".auction-slider-next",
			prevEl: ".auction-slider-prev",
		},

		breakpoints: {
			280: {
				slidesPerView: 1,
			},
			386: {
				slidesPerView: 1,
			},
			576: {
				slidesPerView: 1,
			},
			768: {
				slidesPerView: 2,
			},
			992: {
				slidesPerView: 3,
			},
			1200: {
				slidesPerView: 4,
			},
			1400: {
				slidesPerView: 4,
			},
		},
	});
	// Home1 auction Slider
	var swiper = new Swiper(".home1-category-slider", {
		slidesPerView: 1,
		speed: 1500,
		spaceBetween: 25,
		pauseOnMouseEnter: true,
		autoplay: {
			delay: 2500,
			disableOnInteraction: false,
		},
		navigation: {
			nextEl: ".category-slider-next",
			prevEl: ".category-slider-prev",
		},

		breakpoints: {
			280: {
				slidesPerView: 1,
			},
			375: {
				slidesPerView: 2,
				spaceBetween: 15,
			},
			576: {
				slidesPerView: 3,
				spaceBetween: 15,
			},
			768: {
				slidesPerView: 4,
			},
			992: {
				slidesPerView: 5,
				spaceBetween: 15,
			},
			1200: {
				slidesPerView: 6,
			},
			1400: {
				slidesPerView: 6,
			},
		},
	});

	var swiper = new Swiper(".home1-banner2-slider", {
		slidesPerView: 1,
		spaceBetween: 30,
		speed: 2000,
		loop: true,
		effect: "fade",
		fadeEffect: {
			crossFade: true,
		},
		pagination: {
			el: ".swiper-pagination2",
			clickable: true,
		},
	});

	var swiper = new Swiper(".home1-testimonial-slider", {
		slidesPerView: 1,
		spaceBetween: 10,
		speed: 1500,
		effect: 'fade', // Use the fade effect
		fadeEffect: {
			crossFade: true // Enable cross-fade transition
		},
		pauseOnMouseEnter: true,
		autoplay: {
			delay: 2500,
			disableOnInteraction: false,
		},
		navigation: {
			nextEl: ".testimonial-slider-next",
			prevEl: ".testimonial-slider-prev",
		},
	});
	// Home2 Banner Slider
	var swiper = new Swiper(".home2-banner-slider", {
		slidesPerView: 1,
		speed: 1500,
		spaceBetween: 25,
		slidesPerView: 1,
		centerSlides: true,
		loop: true,
		effect: 'fade',
		pauseOnMouseEnter: true,
		autoplay: {
			delay: 3000,
			disableOnInteraction: false,
		},
		navigation: {
			nextEl: ".next-4",
			prevEl: ".prev-4",
		},
		pagination: {
			el: ".paginations1",
			clickable: true,
		},
	});
	// Home2 Banner2 Slider
	var swiper = new Swiper(".home2-banner2-slider", {
		slidesPerView: 1,
		speed: 1500,
		spaceBetween: 25,
		slidesPerView: 1,
		loop: true,
		pauseOnMouseEnter: true,
		effect: 'fade',
		fadeEffect: {
			crossFade: true // Enable cross-fade transition
		},
		autoplay: {
			delay: 3000,
			disableOnInteraction: false,
		},
		pagination: {
			el: ".pagination2",
			clickable: true,
		},
	});
	// Home2 Upcoming auction Slider
	var swiper = new Swiper(".home2-upcoming-auction-slider", {
		slidesPerView: 1,
		speed: 1500,
		spaceBetween: 15,
		pauseOnMouseEnter: true,
		autoplay: {
			delay: 2500,
			disableOnInteraction: false,
		},
		pagination: {
			el: ".progress-pagination",
			type: "progressbar",
		},
		navigation: {
			nextEl: ".upcoming-slider-next",
			prevEl: ".upcoming-slider-prev",
		},

		breakpoints: {
			280: {
				slidesPerView: 1,
			},
			386: {
				slidesPerView: 1,
			},
			576: {
				slidesPerView: 1,
			},
			768: {
				slidesPerView: 2,
			},
			992: {
				slidesPerView: 2,
			},
			1200: {
				slidesPerView: 3,
			},
			1400: {
				slidesPerView: 4,
			},
		},
	});
	// Home3 Category Slider
	var swiper = new Swiper(".home3-category-slider", {
		slidesPerView: 1,
		speed: 1500,
		spaceBetween: 15,
		navigation: {
			nextEl: ".category-slider-next",
			prevEl: ".category-slider-prev",
		},
		breakpoints: {
			280: {
				slidesPerView: 1,
			},
			375: {
				slidesPerView: 1,
				spaceBetween: 15,
			},
			576: {
				slidesPerView: 2,
				spaceBetween: 15,
			},
			768: {
				slidesPerView: 3,
			},
			992: {
				slidesPerView: 4,
				spaceBetween: 15,
			},
			1200: {
				slidesPerView: 5,
			},
			1400: {
				slidesPerView: 5,
			},
		},
	});
	// Home2 Upcoming auction Slider
	var swiper = new Swiper(".home2-popular-auction-slider", {
		slidesPerView: 1,
		speed: 1500,
		spaceBetween: 15,
		pagination: {
			el: ".progress-pagination2",
			type: "progressbar",
		},
		breakpoints: {
			280: {
				slidesPerView: 1,
			},
			386: {
				slidesPerView: 1,
			},
			576: {
				slidesPerView: 1,
			},
			768: {
				slidesPerView: 2,
			},
			992: {
				slidesPerView: 2,
			},
			1200: {
				slidesPerView: 3,
			},
			1400: {
				slidesPerView: 3,
			},
		},
	});
	// Home2 Testimonial Slider
	var swiper = new Swiper(".home2-testimonial-slider", {
		slidesPerView: 1,
		speed: 1500,
		spaceBetween: 25,
		autoplay: {
			delay: 2500,
			disableOnInteraction: false,
		},
		navigation: {
			nextEl: ".home2-testimonial-slider-next",
			prevEl: ".home2-testimonial-slider-prev",
		},
		breakpoints: {
			280: {
				slidesPerView: 1,
			},
			386: {
				slidesPerView: 1,
			},
			576: {
				slidesPerView: 1,
			},
			768: {
				slidesPerView: 2,
			},
			992: {
				slidesPerView: 2,
			},
			1200: {
				slidesPerView: 3,
			},
			1400: {
				slidesPerView: 3,
			},
		},
	});
	// Home3 Testimonial Slider
	var swiper = new Swiper(".home3-testimonial-slider", {
		slidesPerView: 1,
		speed: 1500,
		spaceBetween: 25,
		effect: 'fade',
		fadeEffect: {
			crossFade: true // Enable cross-fade transition
		},
		pauseOnMouseEnter: true,
		autoplay: {
			delay: 2500,
			disableOnInteraction: false,
		},
		navigation: {
			nextEl: ".home3-testimonial-slider-next",
			prevEl: ".home3-testimonial-slider-prev",
		},
	});
	// Home4 Category Slider
	var swiper = new Swiper(".home4-banner-img-slider", {
		slidesPerView: 1,
		speed: 1500,
		spaceBetween: 15,
		effect: 'fade',
		fadeEffect: {
			crossFade: true // Enable cross-fade transition
		},
		pauseOnMouseEnter: true,
		autoplay: {
			delay: 2500,
			disableOnInteraction: false,
		},
		navigation: {
			nextEl: ".home4-banner-img-slider-next",
			prevEl: ".home4-banner-img-slider-prev",
		},
		pagination: {
			el: ".paginations1",
			type: "fraction",
		},
	});
	// Home4 Category Slider
	var swiper = new Swiper(".home4-category-slider", {
		slidesPerView: 1,
		speed: 1500,
		spaceBetween: 15,
		navigation: {
			nextEl: ".category-slider-next",
			prevEl: ".category-slider-prev",
		},

		breakpoints: {
			280: {
				slidesPerView: 1,
			},
			375: {
				slidesPerView: 1,
				spaceBetween: 15,
			},
			576: {
				slidesPerView: 2,
				spaceBetween: 15,
			},
			768: {
				slidesPerView: 3,
			},
			992: {
				slidesPerView: 4,
				spaceBetween: 15,
			},
			1200: {
				slidesPerView: 5,
			},
			1400: {
				slidesPerView: 5,
			},
		},
	});
	// Home4 auction Slider
	var swiper = new Swiper(".home4-process-slider", {
		slidesPerView: 1,
		speed: 1500,
		spaceBetween: 25,
		breakpoints: {
			280: {
				slidesPerView: 1,
			},
			386: {
				slidesPerView: 1,
			},
			576: {
				slidesPerView: 1,
			},
			768: {
				slidesPerView: 2,
			},
			992: {
				slidesPerView: 3,
			},
			1200: {
				slidesPerView: 3,
			},
			1400: {
				slidesPerView: 3,
			},
		},
	});
	// Home4 auction Slider
	var swiper = new Swiper(".home4-auction-close-slider", {
		slidesPerView: 1,
		speed: 1500,
		spaceBetween: 25,
		pauseOnMouseEnter: true,
		autoplay: {
			delay: 2500,
			disableOnInteraction: false,
		},
		navigation: {
			nextEl: ".auction-close-slider-next",
			prevEl: ".auction-close-slider-prev",
		},
		breakpoints: {
			280: {
				slidesPerView: 1,
			},
			386: {
				slidesPerView: 1,
			},
			576: {
				slidesPerView: 1,
			},
			768: {
				slidesPerView: 2,
			},
			992: {
				slidesPerView: 3,
			},
			1200: {
				slidesPerView: 4,
			},
			1400: {
				slidesPerView: 4,
			},
		},
	});
	// Home5 Banner Slider
	var swiper = new Swiper(".home5-banner-slider", {
		slidesPerView: 1,
		speed: 1500,
		spaceBetween: 25,
		slidesPerView: 1,
		centerSlides: true,
		loop: true,
		effect: "fade",
		pauseOnMouseEnter: true,
		fadeEffect: {
			crossFade: true,
		},
		autoplay: {
			delay: 3000,
			disableOnInteraction: false,
		},
		navigation: {
			nextEl: ".home5-banner-slider-next",
			prevEl: ".home5-banner-slider-prev",
		},
		pagination: {
			el: ".paginations1",
			clickable: true,
		},
	});
	// Home5 Process Slider
	var swiper = new Swiper(".home5-process-slider", {
		slidesPerView: 1,
		speed: 1500,
		spaceBetween: 15,
		pauseOnMouseEnter: true,
		autoplay: {
			delay: 2500,
			disableOnInteraction: false,
		},
		pagination: {
			el: ".progress-pagination",
			type: "progressbar",
		},
		navigation: {
			nextEl: ".home5-process-slider-next",
			prevEl: ".home5-process-slider-prev",
		},

		breakpoints: {
			280: {
				slidesPerView: 1,
			},
			386: {
				slidesPerView: 1,
			},
			576: {
				slidesPerView: 1,
			},
			768: {
				slidesPerView: 2,
			},
			992: {
				slidesPerView: 2,
			},
			1200: {
				slidesPerView: 3,
			},
			1400: {
				slidesPerView: 3,
			},
		},
	});
	// Home5 Category Slider
	var swiper = new Swiper(".home5-category-slider", {
		slidesPerView: 1,
		speed: 1500,
		spaceBetween: 15,
		navigation: {
			nextEl: ".category-slider-next",
			prevEl: ".category-slider-prev",
		},
		breakpoints: {
			280: {
				slidesPerView: 1,
			},
			375: {
				slidesPerView: 1,
				spaceBetween: 15,
			},
			576: {
				slidesPerView: 2,
				spaceBetween: 15,
			},
			768: {
				slidesPerView: 3,
			},
			992: {
				slidesPerView: 4,
				spaceBetween: 15,
			},
			1200: {
				slidesPerView: 5,
			},
			1400: {
				slidesPerView: 6,
			},
		},
	});
	// Home6 Testimonial Slider
	var swiper = new Swiper(".home6-testimonial-slider", {
		slidesPerView: 1,
		speed: 1500,
		spaceBetween: 25,
		navigation: {
			nextEl: ".home6-testimonial-slider-next",
			prevEl: ".home6-testimonial-slider-prev",
		},

		breakpoints: {
			280: {
				slidesPerView: 1,
			},
			386: {
				slidesPerView: 1,
			},
			576: {
				slidesPerView: 1,
			},
			768: {
				slidesPerView: 1,
			},
			992: {
				slidesPerView: 2,
			},
			1200: {
				slidesPerView: 2,
			},
			1400: {
				slidesPerView: 2,
			},
		},
	});
	// Home6 Blog Slider
	var swiper = new Swiper(".home6-blog-slider", {
		slidesPerView: 1,
		speed: 1500,
		spaceBetween: 15,
		pauseOnMouseEnter: true,
		autoplay: {
			delay: 2500,
			disableOnInteraction: false,
		},
		pagination: {
			el: ".paginations1",
			clickable: true,
		},
		breakpoints: {
			280: {
				slidesPerView: 1,
			},
			375: {
				slidesPerView: 1,
				spaceBetween: 15,
			},
			576: {
				slidesPerView: 1,
				spaceBetween: 15,
			},
			768: {
				slidesPerView: 2,
			},
			992: {
				slidesPerView: 3,
				spaceBetween: 15,
			},
			1200: {
				slidesPerView: 3,
			},
			1400: {
				slidesPerView: 3,
			},
		},
	});
	// Home7 auction Slider
	var swiper = new Swiper(".home7-auction-slider", {
		slidesPerView: 1,
		speed: 1500,
		spaceBetween: 25,
		navigation: {
			nextEl: ".home7-auction-slider-next",
			prevEl: ".home7-auction-slider-prev",
		},

		breakpoints: {
			280: {
				slidesPerView: 1,
			},
			386: {
				slidesPerView: 1,
			},
			576: {
				slidesPerView: 1,
			},
			768: {
				slidesPerView: 2,
			},
			992: {
				slidesPerView: 3,
			},
			1200: {
				slidesPerView: 4,
			},
			1400: {
				slidesPerView: 4,
			},
			1600: {
				slidesPerView: 5,
			},
		},
	});
	// Home7 New Arrrival auction Slider
	var swiper = new Swiper(".home7-new-arrival-slider", {
		slidesPerView: 1,
		speed: 1500,
		spaceBetween: 25,
		navigation: {
			nextEl: ".home7-new-arrival-slider-next",
			prevEl: ".home7-new-arrival-slider-prev",
		},
		breakpoints: {
			280: {
				slidesPerView: 1,
			},
			386: {
				slidesPerView: 1,
			},
			576: {
				slidesPerView: 1,
			},
			768: {
				slidesPerView: 2,
			},
			992: {
				slidesPerView: 3,
			},
			1200: {
				slidesPerView: 4,
			},
			1400: {
				slidesPerView: 4,
			},
			1600: {
				slidesPerView: 5,
			},
		},
	});
	// Home7 Banner2 Slider
	var swiper = new Swiper(".home7-banner2-slider", {
		slidesPerView: 1,
		speed: 1500,
		spaceBetween: 15,
		pauseOnMouseEnter: true,
		autoplay: {
			delay: 2500,
			disableOnInteraction: false,
		},
		pagination: {
			el: ".paginations1",
			clickable: true,
		},
		breakpoints: {
			280: {
				slidesPerView: 1,
			},
			375: {
				slidesPerView: 1,
				spaceBetween: 15,
			},
			576: {
				slidesPerView: 1,
				spaceBetween: 15,
			},
			768: {
				slidesPerView: 1,
			},
			992: {
				slidesPerView: 2,
				spaceBetween: 15,
			},
			1200: {
				slidesPerView: 2,
			},
			1400: {
				slidesPerView: 2,
			},
		},
	});
	// Home7 Blog Slider
	var swiper = new Swiper(".home7-blog-slider", {
		slidesPerView: 1,
		speed: 1500,
		spaceBetween: 25,
		navigation: {
			nextEl: ".home7-blog-slider-next",
			prevEl: ".home7-blog-slider-prev",
		},
		breakpoints: {
			280: {
				slidesPerView: 1,
			},
			386: {
				slidesPerView: 1,
			},
			576: {
				slidesPerView: 1,
			},
			768: {
				slidesPerView: 2,
			},
			992: {
				slidesPerView: 3,
			},
			1200: {
				slidesPerView: 4,
			},
			1400: {
				slidesPerView: 4,
			},
		},
	});

	// Post Format Gallery Blog Slider
	var swiper = new Swiper(".blog-archive-slider", {
		slidesPerView: 1,
		speed: 1500,
		loop: true,
		navigation: {
			nextEl: ".blog1-next ",
			prevEl: ".blog1-prev",
		},
	});
	// Home5 Category Slider
	var swiper = new Swiper(".auction-details-nav-slider", {
		slidesPerView: 1,
		speed: 1500,
		spaceBetween: 15,
		grabCursor: true,
		pauseOnMouseEnter: true,
		autoplay: {
			delay: 2500,
			disableOnInteraction: false,
		},
		navigation: {
			nextEl: ".category-slider-next",
			prevEl: ".category-slider-prev",
		},
		breakpoints: {
			280: {
				slidesPerView: 2,
			},
			350: {
				slidesPerView: 3,
				spaceBetween: 10,
			},
			576: {
				slidesPerView: 3,
				spaceBetween: 15,
			},
			768: {
				slidesPerView: 4,
			},
			992: {
				slidesPerView: 5,
				spaceBetween: 15,
			},
			1200: {
				slidesPerView: 5,
			},
			1400: {
				slidesPerView: 5,
			},
		},
	});

	// scroll up button
	if (document.querySelector(".circle-container")) {
		document.addEventListener("DOMContentLoaded", function (event) {
			let offset = 50;
			let circleContainer = document.querySelector(".circle-container");
			let circlePath = document.querySelector(".circle-container path");
			let pathLength = circlePath.getTotalLength();
			circlePath.style.transition = circlePath.style.WebkitTransition = "none";
			circlePath.style.strokeDasharray = pathLength;
			circlePath.style.strokeDashoffset = pathLength;
			circlePath.getBoundingClientRect();
			circlePath.style.transition = circlePath.style.WebkitTransition =
				"stroke-dashoffset 10ms linear";

			let updateLoader = () => {
				let scrollTop = window.scrollY;
				let docHeight = document.body.offsetHeight;
				let winHeight = window.innerHeight;
				let height = docHeight - winHeight;
				let progress = pathLength - (scrollTop * pathLength) / height;
				circlePath.style.strokeDashoffset = progress;

				if (scrollTop > offset) {
					circleContainer.classList.add("active");
				} else {
					circleContainer.classList.remove("active");
				}
			};
			circleContainer.onclick = function () {
				window.scrollTo({
					top: 0,
					behavior: "smooth"
				});
			};

			window.onscroll = () => {
				updateLoader();
			};
			updateLoader();
		});
	}

	// Language Btn
	$(".language-btn").on("click", function (e) {
		let parent = $(this).parent();
		parent.find(".language-list").toggleClass("active");
		e.stopPropagation();
	});
	$(document).on("click", function (e) {
		if (!$(e.target).closest(".language-btn").length) {
			$(".language-list").removeClass("active");
		}
	});
	// Serch Btn
	$(".search-btn").on("click", function (e) {
		let parent = $(this).parent();
		parent.find(".search-input").toggleClass("active");
		e.stopPropagation();
	});
	$(document).on("click", function (e) {
		if (!$(e.target).closest(".search-input, .search-btn, .sidebar-menu, .menu-icon").length) {
			$(".search-input").removeClass("active");
			$('.sidebar-menu').removeClass('show-menu');
		}
	});
	$(".search-close").on("click", function (e) {
		$(".search-input").removeClass("active");
	});


	// BTN Hover
	$(".btn-hover")
		.on("mouseenter", function (e) {
			var parentOffset = $(this).offset(),
				relX = e.pageX - parentOffset.left,
				relY = e.pageY - parentOffset.top;
			$(this).find("span").css({
				top: 0,
				left: 0
			});
			$(this).find("span").css({
				top: relY,
				left: relX
			});
		})
		.on("mouseout", function (e) {
			var parentOffset = $(this).offset(),
				relX = e.pageX - parentOffset.left,
				relY = e.pageY - parentOffset.top;
			$(this).find("span").css({
				top: 0,
				left: 0
			});
			$(this).find("span").css({
				top: relY,
				left: relX
			});
		});

	// timer start
	$("[data-countdown]").each(function () {
		var $deadline = new Date($(this).data("countdown")).getTime();
		var $dataDays = $(this).children("[data-days]");
		var $dataHours = $(this).children("[data-hours]");
		var $dataMinutes = $(this).children("[data-minutes]");
		var $dataSeconds = $(this).children("[data-seconds]");
		var x = setInterval(function () {
			var now = new Date().getTime();
			var t = $deadline - now;
			var days = Math.floor(t / (1000 * 60 * 60 * 24));
			var hours = Math.floor((t % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
			var minutes = Math.floor((t % (1000 * 60 * 60)) / (1000 * 60));
			var seconds = Math.floor((t % (1000 * 60)) / 1000);
			$dataDays.html(`${days} <span>Days</span> <span>Days</span>`);
			$dataHours.html(`${hours} <span>Hours</span> <span>Hours</span>`);
			$dataMinutes.html(`${minutes} <span>Mint</span> <span>Minutes</span>`);
			$dataSeconds.html(`${seconds} <span>Sec</span> <span>Seconds</span>`);
			if (t <= 0) {
				clearInterval(x);
				$dataDays.html("00 <span>Days</span> <span>Days</span>");
				$dataHours.html("00 <span>Hours</span> <span>Hours</span>");
				$dataMinutes.html("00 <span>Mint</span> <span>Minutes</span>");
				$dataSeconds.html("00 <span>Sec</span> <span>Seconds</span>");
			}
		}, 1000);
	});

	//list grid view
	$(".grid-view li").on("click", function () {
		// Get the class of the clicked li element
		var clickedClass = $(this).attr("class");
		// Extract the class name without "item-" prefix
		var className = clickedClass.replace("item-", "");
		// Add a new class to the target div and remove old classes
		var targetDiv = $(".list-grid-product-wrap");
		targetDiv.removeClass().addClass("list-grid-product-wrap " + className + "-wrapper");
		// Remove the 'selected' class from siblings and add it to the clicked element
		$(this).siblings().removeClass("active");
		$(this).addClass("active");
	});

	// sidebar
	$(".filter").on("click", function (e) {
		e.stopPropagation();
		$(".filter-sidebar, .filter-top").toggleClass("slide");
	});
	$(document).on("click", function (e) {
		if (!$(e.target).closest(".filter-sidebar, .filter-top, .filter").length) {
			$(".filter-sidebar, .filter-top").removeClass("slide");
		}
	});

	// Handle click on the input item
	$('.select-input').on("click", function () {
		$('.custom-select-wrap').toggleClass('active');
	});
	$('.searchbox-input').each(function () {
		var $container = $(this);
		$container.find('.option-list li').on("click", function () {
			var destinationText = $(this).find('.destination h6, h6').text();
			$container.find('.select-input input').val(destinationText);
			$container.find('.custom-select-wrap').removeClass('active');
		});
		$(document).on("click", function (event) {
			if (!$(event.target).closest($container).length) {
				$container.find('.custom-select-wrap').removeClass('active');
			}
		});
		$container.find('.custom-select-search-area input').on('input', function () {
			var searchText = $(this).val().toLowerCase();
			$container.find('.option-list li').each(function () {
				var destinationText = $(this).find('.destination h6').text().toLowerCase();
				if (destinationText.includes(searchText)) {
					$(this).show();
				} else {
					$(this).hide();
				}
			});
		});
	});



	//wow js 
	jQuery(window).on('load', function () {
		new WOW().init();
		window.wow = new WOW({
			boxClass: 'wow',
			animateClass: 'animated',
			offset: 0,
			mobile: true,
			live: true,
			offset: 80
		})
		window.wow.init();
	});

	///Marquee
	const marquee = document.querySelectorAll(".marquee_text");
	if (marquee) {
		$(".marquee_text").marquee({
			direction: "left",
			duration: 25000,
			gap: 50,
			delayBeforeStart: 0,
			duplicated: true,
			startVisible: true,
		});
	}


	// Auction timer js from simple auction 
	function closeAuction() {
		var auctionid = jQuery(this).data('auctionid');
		var future = jQuery(this).hasClass('future') ? 'true' : 'false';
		var ajaxcontainer = jQuery(this).parent().next('.auction-ajax-change');
		if (ajaxcontainer.length == 0) {
			ajaxcontainer = jQuery(".auction_form[data-product_id='" + auctionid + "']");
		}
		ajaxcontainer.hide();
		jQuery('<div class="ajax-working"></div>').insertBefore(ajaxcontainer);
		ajaxcontainer.parent().children('form.buy-now').hide();

		var ajaxurl = saajaxurl + '=finish_auction';

		jQuery(document.body).trigger('sa-close-auction', [auctionid]);
		var request = jQuery.ajax({
			type: "post",
			url: ajaxurl,
			cache: false,
			data: {
				action: "finish_auction",
				post_id: auctionid,
				ret: ajaxcontainer.length,
				future: future
			},
			success: function (response) {
				if (response) {
					if (response.status == 'closed') {
						ajaxcontainer.parent().children('form.buy-now').remove();
						if (response.message) {
							jQuery('.ajax-working').remove();
							jQuery('.main-auction.auction-time-countdown[data-auctionid=' + auctionid + ']').parent().remove();
							ajaxcontainer.empty().prepend(response.message).wrap("<div></div>");
							ajaxcontainer.show();
							jQuery(document.body).trigger('sa-action-closed', [auctionid]);
						}
					} else if (response.status == 'running') {
						getPriceAuction();
						jQuery('.ajax-working').remove();
						ajaxcontainer.show();
						ajaxcontainer.parent().children('form.buy-now').show();
					} else {
						location.reload();
					}
				} else {
					location.reload();
				}

			},
			error: function () {
				location.reload();
			},
		});

	}

	// Auction timer run after ajax 
	function timer_run_after_success() {
		$(document).find('.auction-time-countdown').each(function (index) {
			console.log(this);
			var time = $(this).data('time');
			var format = $(this).data('format');
			var compact = false;

			if (format === '') {
				format = 'yowdHMS';
			}

			if (data.compact_counter === 'yes' || $(this).data('compact') === true) {
				compact = true;
			} else {
				compact = false;
			}
			var etext = '';
			$(this).SAcountdown({
				until: time,
				format: format,
				compact: compact,

				onExpiry: closeAuction,
				expiryText: etext
			});
			if ($(this).hasClass('future')) {
				etext = '<div class="started">' + data.started + '</div>';
			} else {
				etext = '<div class="over">' + data.checking + '</div>';
			}

			if (!$('body').hasClass('logged-in')) {
				time = $.SAcountdown.UTCDate(-(new Date().getTimezoneOffset()), new Date(time * 1000));
			}
		});
	}

	// Quick View Button Ajax 
	$('.quick-view-button').on('click', function (e) {
		e.preventDefault();

		var product_id = $(this).data('product_id');

		$.ajax({
			url: load_more_params.ajaxurl,
			type: 'POST',
			data: {
				action: 'custom_quick_view',
				product_id: product_id
			},
			success: function (response) {
				// Append the response to the modal or quick view container
				$('#quick-view-modal .modal-content').html(response);
				$('#quick-view-modal').show();
			}
		});
	});
	// Close modal
	$('#quick-view-modal .close').on('click', function () {
		$('#quick-view-modal').hide();
	});


	// Price low to hight, hight to low Filter 
	$('#product-sorting').on('change', function () {

		var pageTemplate = $('body').attr('class').match(/page-template-([^\s]+)/)[1]; // Gets the template name from body class

		var sort_by = $(this).val();

		$.ajax({
			url: load_more_params.ajaxurl, // WooCommerce AJAX URL
			type: 'POST',
			data: {
				action: 'filter_products',
				orderby: sort_by,
				page_template: pageTemplate
			},
			beforeSend: function () {
				$('#product-data').parent('div').addClass('egns-loading');
			},
			success: function (response) {
				$('#product-data').html(response); // Replace product list with sorted products

				// Auction timer run after ajax 
				timer_run_after_success();

				$('#product-data').parent('div').removeClass('egns-loading');

			},
			error: function () {
				$('#product-data').html('<p>An error occurred. Please try again.</p>');
			}
		});
	});


	// Type Of Sales  
	$('#auction-filters input[type="checkbox"]').on('change', function () {

		var pageTemplate = $('body').attr('class').match(/page-template-([^\s]+)/)[1]; // Gets the template name from body class

		var filters = [];
		$('#auction-filters input[type="checkbox"]:checked').each(function () {
			filters.push($(this).data('filter'));
		});

		$.ajax({
			url: load_more_params.ajaxurl, // WordPress AJAX URL
			type: 'POST',
			data: {
				action: 'filter_auction_items', // The action in PHP to handle this request
				filters: filters,
				page_template: pageTemplate
			},
			beforeSend: function () {
				$('#product-data').parent('div').addClass('egns-loading');
			},
			success: function (response) {
				$('#product-data').html(response); // Load the filtered products
				// Auction timer run after ajax 
				timer_run_after_success();

				$('#product-data').parent('div').removeClass('egns-loading');

				$('#paginationData').hide();
			}
		});
	});

	// Product Category 
	$('#product-categories input[type="checkbox"]').on('change', function () {

		var pageTemplate = $('body').attr('class').match(/page-template-([^\s]+)/)[1]; // Gets the template name from body class

		var selectedCategories = [];
		$('#product-categories input[type="checkbox"]:checked').each(function () {
			selectedCategories.push($(this).data('filter'));
		});

		$.ajax({
			url: load_more_params.ajaxurl, // WordPress AJAX URL
			type: 'POST',
			data: {
				action: 'filter_cat_products_ajax', // The action in PHP to handle this request
				categories: selectedCategories,
				page_template: pageTemplate
			},
			beforeSend: function () {
				$('#product-data').parent('div').addClass('egns-loading');
			},
			success: function (response) {
				$('#product-data').html(response);
				// Auction timer run after ajax 
				timer_run_after_success();

				$('#product-data').parent('div').removeClass('egns-loading');

				$('#paginationData').hide();
			}
		});
	});

	// Product search
	function performSearch() {

		var pageTemplate = $('body').attr('class').match(/page-template-([^\s]+)/)[1]; // Gets the template name from body class
		var searchTerm = $('.search-box input').val();

		if (searchTerm.length > 0) {
			$.ajax({
				url: load_more_params.ajaxurl,
				type: 'POST',
				data: {
					action: 'ajax_search_products',
					search_term: searchTerm,
					page_template: pageTemplate,
					paged: 1 // Reset pagination on new search
				},
				beforeSend: function () {
					$('#product-data').parent('div').addClass('egns-loading');
				},
				success: function (response) {
					// Update the output container with the response
					$('#product-data').html(response);

					// Auction timer run after ajax 
					timer_run_after_success();

					$('#product-data').parent('div').removeClass('egns-loading');

					$('#paginationData').hide();
				},
				error: function () {
					$('#product-data').html('<p>An error occurred. Please try again.</p>');
				}
			});
		}
	}

	// Trigger search on button click
	$('.search-box button').on('click', function (e) {
		e.preventDefault();
		performSearch();
	});

	// Trigger search on input (every key press)
	$('.search-box input').on('input', function () {
		performSearch();
	});

	// Trigger search on pressing Enter key
	$('.search-box input').on('keypress', function (e) {
		if (e.which === 13) { // 13 is the Enter key
			e.preventDefault();
			performSearch();
		}
	});
	// End Product search


	// Product item condition 
	$('.single-item.condition').on('click', function () {

		var pageTemplate = $('body').attr('class').match(/page-template-([^\s]+)/)[1]; // Gets the template name from body class

		// Get the selected value
		var selectedValue = $(this).data('value');

		var textWithoutSpaces = $(this).text().replace(/\s+/g, ''); //remove all space from text

		$('#auction-product-status').val(textWithoutSpaces); // Update the input with the selected text

		// AJAX call
		$.ajax({
			url: load_more_params.ajaxurl, // Use the localized variable for AJAX URL
			type: 'POST',
			data: {
				action: 'fetch_auction_products', // The action to call
				status: selectedValue, // The value to send
				page_template: pageTemplate,
			},
			beforeSend: function () {
				$('#product-data').parent('div').addClass('egns-loading');
			},
			success: function (response) {
				// Display the returned auction products
				$('#product-data').html(response);

				// Auction timer run after ajax 
				timer_run_after_success();

				$('#product-data').parent('div').removeClass('egns-loading');

				$('#paginationData').hide();
			},
			error: function (error) {
				console.error('AJAX Error:', error);
			}
		});
	});



	// Product period selection
	$('.option-list .single-item.period').on('click', function () {

		var pageTemplate = $('body').attr('class').match(/page-template-([^\s]+)/)[1]; // Gets the template name from body class

		var selectedPeriod = $(this).data('period');
		var periodText = $(this).find('h6').text();
		$('#selected-period').val(periodText);

		// Perform AJAX request to filter products by selected period
		$.ajax({
			url: load_more_params.ajaxurl, // Add the AJAX URL from WordPress
			type: 'POST',
			data: {
				action: 'filter_auction_products', // Define the action
				period: selectedPeriod,
				page_template: pageTemplate,
			},
			beforeSend: function () {
				$('#product-data').parent('div').addClass('egns-loading');
			},
			success: function (response) {
				// Replace the current auction product list with the new filtered products
				$('#product-data').html(response);

				// Auction timer run after ajax 
				timer_run_after_success();

				$('#product-data').parent('div').removeClass('egns-loading');

				$('#paginationData').hide();
			}
		});
	});


	// Elementor hightlight widget ajax 
	$('#cat-sort').on('change', function () {

		var cat = $(this).val();

		$.ajax({
			url: load_more_params.ajaxurl, // WooCommerce AJAX URL
			type: 'POST',
			data: {
				action: 'highlight_auction',
				cat,
			},
			beforeSend: function () {
				$('#product-data').parent('div').addClass('egns-loading');
			},
			success: function (response) {
				$('#cat-sorting').html(response); // Replace product list with sorted products

				// Auction timer run after ajax 
				timer_run_after_success();

				$('#product-data').parent('div').removeClass('egns-loading');
			},
			error: function () {
				$('#cat-sorting').html('<p>An error occurred. Please try again.</p>');
			}
		});

	});



}(jQuery));