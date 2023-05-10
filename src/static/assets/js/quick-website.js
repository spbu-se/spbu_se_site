/*

Theme: Quick – Website UI Kit
Version: 1.1.1
Product Page: https://themes.getbootstrap.com/product/quick-website-ui-kit-2/
License: https://themes.getbootstrap.com/licenses/
Author: Webpixels
Author URI: https://webpixels.io

---

Copyright 2020 Webpixels

*/

// //
// // Layout
// //
//
// 'use strict';
//
// var Layout = (function() {
//
//     function pinSidenav($this) {
//         $('.sidenav-toggler').addClass('active');
//         $('.sidenav-toggler').data('action', 'sidenav-unpin');
//         $('body').addClass('sidenav-pinned ready');
//         $('body').find('.main-content').append('<div class="sidenav-mask mask-body d-xl-none" data-action="sidenav-unpin" data-target='+$this.data('target')+' />');
//
//         var $sidenav = $($this.data('target'));
//
//         $sidenav.addClass('show');
//
//         // Store the sidenav state in a cookie session
//         localStorage.setItem('sidenav-state', 'pinned');
//
//         // alert('pinned')
//     }
//
//     function unpinSidenav($this) {
//         $('.sidenav-toggler').removeClass('active');
//         $('.sidenav-toggler').data('action', 'sidenav-pin');
//         $('body').removeClass('sidenav-pinned');
//         $('body').addClass('ready')
//         $('body').find('.sidenav-mask').remove();
//
//         var $sidenav = $($this.data('target'));
//
//         $sidenav.removeClass('show');
//
//         // Store the sidenav state in a cookie session
//         localStorage.setItem('sidenav-state', 'unpinned');
//
//         // alert('unpinned')
//     }
//
//     // Set sidenav state from cookie
//
//     var $sidenavState = localStorage.getItem('sidenav-state') ? localStorage.getItem('sidenav-state') : 'pinned';
//
// 	$(window).on({
// 		'load resize': function() {
//             if($('.sidenav-toggler').length) {
//                 if($(window).width() < 1200) {
//                     unpinSidenav($('.sidenav-toggler'));
//                 } else {
//                     if($sidenavState == 'pinned') {
//                         pinSidenav($('.sidenav-toggler'));
//                     }
//                     else if($sidenavState == 'unpinned') {
//                         unpinSidenav($('.sidenav-toggler'));
//                     }
//                 }
//             } else {
//                 $('body').addClass('ready');
//             }
// 		}
// 	})
//
//     $("body").on("click", "[data-action]", function(e) {
//
//         e.preventDefault();
//
//         var $this = $(this);
//         var action = $this.data('action');
//         var target = $this.data('target');
//
//         switch (action) {
//             case "offcanvas-open":
//                 target = $this.data("target"), $(target).addClass("open"), $("body").append('<div class="body-backdrop" data-action="offcanvas-close" data-target=' + target + " />");
//                 break;
//
//             case "offcanvas-close":
//                 target = $this.data("target"), $(target).removeClass("open"), $("body").find(".body-backdrop").remove();
//                 break;
//
//             case 'aside-open':
//                 target = $this.data('target');
//                 $this.addClass('active');
//                 $(target).addClass('show');
//                 $('body').append('<div class="mask-body mask-body-light" data-action="aside-close" data-target='+target+' />');
//                 break;
//
//             case 'aside-close':
//                 target = $this.data('target');
//                 $this.removeClass('active');
//                 $(target).removeClass('show');
//                 $('body').find('.body-backdrop').remove();
//                 break;
//
//             case 'omnisearch-open':
//                 target = $this.data('target');
//                 $this.addClass('active');
//                 $(target).addClass('show');
//                 $(target).find('.form-control').focus();
//                 $('body').addClass('omnisearch-open').append('<div class="mask-body mask-body-dark" data-action="omnisearch-close" data-target="'+target+'" />');
//                 break;
//
//             case 'omnisearch-close':
//                 target = $this.data('target');
//                 $('[data-action="search-open"]').removeClass('active');
//                 $(target).removeClass('show');
//                 $('body').removeClass('omnisearch-open').find('.mask-body').remove();
//                 break;
//
//             case 'search-open':
//                 target = $this.data('target');
//                 $this.addClass('active');
//                 $(target).addClass('show');
//                 $(target).find('.form-control').focus();
//                 break;
//
//             case 'search-close':
//                 target = $this.data('target');
//                 $('[data-action="search-open"]').removeClass('active');
//                 $(target).removeClass('show');
//                 break;
//
//             case 'sidenav-pin':
//                 pinSidenav($this);
//                 break;
//
//             case 'sidenav-unpin':
//                 unpinSidenav($this);
//                 break;
//         }
//     })
//
//     // Add sidenav modifier classes on mouse events
//
//     // $('.sidenav').on('mouseenter', function() {
//     //     if(! $('body').hasClass('g-sidenav-pinned')) {
//     //         $('body').removeClass('g-sidenav-hide').removeClass('g-sidenav-hidden').addClass('g-sidenav-show');
//     //     }
//     // })
//     //
//     // $('.sidenav').on('mouseleave', function() {
//     //     if(! $('body').hasClass('g-sidenav-pinned')) {
//     //         $('body').removeClass('g-sidenav-show').addClass('g-sidenav-hide');
//     //
//     //         setTimeout(function() {
//     //             $('body').removeClass('g-sidenav-hide').addClass('g-sidenav-hidden');
//     //         }, 300);
//     //     }
//     // })
//
//     // Offset an element by giving an existing element's class or id from the same page
//
//     if($('[data-offset-top]').length) {
//         var $el = $('[data-offset-top]'),
//             $offsetEl = $($el.data('offset-top')),
//             offset = $offsetEl.height();
//
//
//         $el.css({'padding-top':offset+'px'})
//     }
// })();

//
// Popover
//

'use strict';

var PopoverHover = (function() {

	// Variables

	var $popover = $('[data-toggle="popoverhover"]');


	// Methods

	function init($this) {
		var popoverClass = '';

		if ($this.data('color')) {
			popoverClass = ' popover-' + $this.data('color');
		}

		var options = {
			trigger: 'hover',
			template:
			'<div class="popover' + popoverClass + '" role="tooltip">'+
				'<div class="arrow"></div>'+
				'<h3 class="popover-header"></h3>' +
				'<div class="popover-body"></div>' +
				'<div class="popover-navigation">' +
					'<button class="btn btn-primary" data-role="prev">« Prev</button>' +
					'<button class="btn btn-primary" data-role="next">Next »</button>' +
					'<button class="btn btn-primary" data-role="end">End tour</button>' +
				'</div>' +
			'</div>'
		};

		$this.popover(options);
	}


	// Events

	if ($popover.length) {
		$popover.each(function() {
			init($(this));
		});
	}

})();


var Popover = (function() {

	// Variables

	var $popover = $('[data-toggle="popover"]');


	// Methods

	function init($this) {
		var popoverClass = '';

		if ($this.data('color')) {
			popoverClass = ' popover-' + $this.data('color');
		}

		var options = {
			trigger: 'focus',
			template:
			'<div class="popover' + popoverClass + '" role="tooltip">'+
				'<div class="arrow"></div>'+
				'<h3 class="popover-header"></h3>' +
				'<div class="popover-body"></div>' +
				'<div class="popover-navigation">' +
					'<button class="btn btn-primary" data-role="prev">« Prev</button>' +
					'<button class="btn btn-primary" data-role="next">Next »</button>' +
					'<button class="btn btn-primary" data-role="end">End tour</button>' +
				'</div>' +
			'</div>'
		};

		$this.popover(options);
		$this.popover('show')
	}


	// Events

	if ($popover.length) {
		$popover.each(function() {
			init($(this));
		});
	}

})();

//
// Style
// Style helper function to get colors and more
//

var PurposeStyle = (function() {

	// Variables

	var style = getComputedStyle(document.body);
    var colors = {
    		gray: {
    			100: '#f6f9fc',
    			200: '#e9ecef',
    			300: '#dee2e6',
    			400: '#ced4da',
    			500: '#adb5bd',
    			600: '#8898aa',
    			700: '#525f7f',
    			800: '#32325d',
    			900: '#212529'
    		},
    		theme: {
    			'primary': style.getPropertyValue('--primary') ? style.getPropertyValue('--primary').replace(' ', '') : '#008aff',
    			'info': style.getPropertyValue('--info') ? style.getPropertyValue('--info').replace(' ', '') : '#50b5ff',
    			'success': style.getPropertyValue('--success') ? style.getPropertyValue('--success').replace(' ', '') : '#5cc9a7',
    			'danger': style.getPropertyValue('--danger') ? style.getPropertyValue('--danger').replace(' ', '') : '#f25767',
    			'warning': style.getPropertyValue('--warning') ? style.getPropertyValue('--warning').replace(' ', '') : '#FFBE3D',
                'dark': style.getPropertyValue('--dark') ? style.getPropertyValue('--dark').replace(' ', '') : '#171347'
    		},
    		transparent: 'transparent',
    	},
		fonts = {
			base: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol"'
		}

	// Return

	return {
		colors: colors,
		fonts: fonts
	};

})();

//
// Sticky
//

'use strict';

var SvgInjector = (function() {

	//
	// Variables
	//

	var $svg = document.querySelectorAll('img.svg-inject');
	var status = false;


	//
	// Methods
	//

	function init($this) {

		var options = {

		};

		SVGInjector($this, options, function(result) {
			status = true
		});
	}


	//
	// Events
	//

	if ($svg.length) {
		init($svg);
	}


	//
	// Return
	//

	return {
		status: status
	};
})();

//
// Tooltip
//

'use strict';

var Tooltip = (function() {

	// Variables

	var $tooltip = $('[data-toggle="tooltip"]');


	// Methods

	function init() {
		$tooltip.tooltip();
	}


	// Events

	if ($tooltip.length) {
		init();
	}

})();

//
// Card
//

'use strict';

// Cookies
/*
var Cookies = (function() {

	// Variables

	var $modal = $("#modal-cookies");


	// Methods

	function show($this) {
        var cookies = localStorage.getItem('modal_cookies');

        if(! cookies) {
            $this.modal('show')
        }
	}

	function hide($this) {
		$this.modal('hide')
	}

	// Events

	if ($modal.length) {
		show($modal);

        $modal.on('hidden.bs.modal', function (e) {
            localStorage.setItem('modal_cookies', 1);
        })
	}

})();

*/

/*
 * Bootstrap Cookie Alert by Wruczek
 * https://github.com/Wruczek/Bootstrap-Cookie-Alert
 * Released under MIT license
 */


(function () {

    var cookieAlert = document.querySelector(".cookiealert");
    var acceptCookies = document.querySelector(".acceptcookies");

    if (!cookieAlert) {
       return;
    }

    cookieAlert.offsetHeight; // Force browser to trigger reflow (https://stackoverflow.com/a/39451131)

    var cookies = localStorage.getItem('modal_cookies');

    // Show the alert if we cant find the "acceptCookies" cookie
    if (! cookies) {
        cookieAlert.classList.add("show");
        //cookieAlert.collapse('show');
    }

    // When clicking on the agree button, create a 1 year
    // cookie to remember user's choice and close the banner
    acceptCookies.addEventListener("click", function () {
        localStorage.setItem('modal_cookies', 1);
        cookieAlert.classList.remove("show");

        // dispatch the accept event
        window.dispatchEvent(new Event("cookieAlertAccept"))
    });
})();

var CopyType = (function() {

	// Variables

	var $element = '.btn-type-clipboard',
		$btn = $($element);


	// Methods

	function init($this) {
		$this.tooltip().on('mouseleave', function() {
			// Explicitly hide tooltip, since after clicking it remains
			// focused (as it's a button), so tooltip would otherwise
			// remain visible until focus is moved away
			$this.tooltip('hide');
		});

		var clipboard = new ClipboardJS($element);

		clipboard.on('success', function(e) {
			$(e.trigger)
				.attr('title', 'Copied!')
				.tooltip('_fixTitle')
				.tooltip('show')
				.attr('title', 'Copy to clipboard')
				.tooltip('_fixTitle')

			e.clearSelection()
		});
	}


	// Events
	if ($btn.length) {
		init($btn);
	}

})();

//
// Demo.js
// only for preview purposes - remove it when starting your project
//

'use strict';

var Demo = (function() {
    $('[data-toggle="sweet-alert"]').on('click', function(){
        var type = $(this).data('sweet-alert');

        switch (type) {
            case 'basic':
                Swal.fire({
                    title: "Here's a message!",
                    text: 'A few words about this sweet alert ...',
                    buttonsStyling: false,
                    confirmButtonClass: 'btn btn-primary'
                })
            break;

            case 'info':
                Swal.fire({
                    title: 'Info',
                    text: 'A few words about this sweet alert ...',
                    type: 'info',
                    buttonsStyling: false,
                    confirmButtonClass: 'btn btn-info'
                })
            break;

            case 'info':
                Swal.fire({
                    title: 'Info',
                    text: 'A few words about this sweet alert ...',
                    type: 'info',
                    buttonsStyling: false,
                    confirmButtonClass: 'btn btn-info'
                })
            break;

            case 'success':
                Swal.fire({
                    title: 'Success',
                    text: 'A few words about this sweet alert ...',
                    type: 'success',
                    buttonsStyling: false,
                    confirmButtonClass: 'btn btn-success'
                })
            break;

            case 'warning':
                Swal.fire({
                    title: 'Warning',
                    text: 'A few words about this sweet alert ...',
                    type: 'warning',
                    buttonsStyling: false,
                    confirmButtonClass: 'btn btn-warning'
                })
            break;

            case 'question':
                Swal.fire({
                    title: 'Are you sure?',
                    text: 'A few words about this sweet alert ...',
                    type: 'question',
                    buttonsStyling: false,
                    confirmButtonClass: 'btn btn-dark'
                })
            break;

            case 'confirm':
                Swal.fire({
                    title: 'Are you sure?',
                    text: "You won't be able to revert this!",
                    type: 'warning',
                    showCancelButton: true,
                    buttonsStyling: false,
                    confirmButtonClass: 'btn btn-danger',
                    confirmButtonText: 'Yes, delete it!',
                    cancelButtonClass: 'btn btn-secondary'
                }).then(function(result) {
                    if (result.value) {
                        // Show confirmation
                        Swal.fire({
                            title: 'Deleted!',
                            text: 'Your file has been deleted.',
                            type: 'success',
                            buttonsStyling: false,
                            confirmButtonClass: 'btn btn-primary'
                        });
                    }
                })
            break;

            case 'image':
                Swal.fire({
                    title: 'Sweet',
                    text: "Modal with a custom image ...",
                    imageUrl: '../../assets/img/prv/splash.png',
                    buttonsStyling: false,
                    confirmButtonClass: 'btn btn-primary',
                    confirmButtonText: 'Super!'
            });
            break;

            case 'timer':
                Swal.fire({
                    title: 'Auto close alert!',
                    text: 'I will close in 2 seconds.',
                    timer: 2000,
                    showConfirmButton: false
                });
            break;
        }
    });
})();

//
// Dropdown
//

'use strict';

var Dropdown = (function() {

	// Variables

	var $dropdown = $('.dropdown-animate'),
		$dropdownSubmenu = $('.dropdown-submenu [data-toggle="dropdown"]');


	// Methods

	function hideDropdown($this) {

		// Add additional .hide class for animated dropdown menus in order to apply some css behind

		var $dropdownMenu = $this.find('.dropdown-menu');

        $dropdownMenu.addClass('hide');

        setTimeout(function(){
            $dropdownMenu.removeClass('hide');
        }, 300);

	}

	function initSubmenu($this) {
        if (!$this.next().hasClass('show')) {
            $this.parents('.dropdown-menu').first().find('.show').removeClass("show");
        }

        var $submenu = $this.next(".dropdown-menu");

        $submenu.toggleClass('show');
        $submenu.parent().toggleClass('show');

        $this.parents('.nav-item.dropdown.show').on('hidden.bs.dropdown', function(e) {
            $('.dropdown-submenu .show').removeClass("show");
        });
	}

	// Events

	if ($dropdown.length) {
    	$dropdown.on({
    		'hide.bs.dropdown': function(e) {
    			hideDropdown($(this));
    		}
    	})
	}

	if ($dropdownSubmenu.length) {
		$dropdownSubmenu.on('click', function(e) {

			initSubmenu($(this))

			return false;
		});
	}


	// Prevent dropdown-menu on closing

	// Stop closing dropdown-menu when clicked inside
    $('.dropdown-menu').on('click', function (event) {
        var events = $._data(document, 'events') || {};

        events = events.click || [];

        for(var i = 0; i < events.length; i++) {
            if(events[i].selector) {

                //Check if the clicked element matches the event selector
                if($(event.target).is(events[i].selector)) {
                    events[i].handler.call(event.target, event);
                }

                // Check if any of the clicked element parents matches the
                // delegated event selector (Emulating propagation)
                $(event.target).parents(events[i].selector).each(function(){
                    events[i].handler.call(this, event);
                });
            }
        }

        event.stopPropagation();
    });
})();

//
// Forms
//

'use strict';


//
// Form control
//

var FormControl = (function() {

	// Variables

	var $input = $('.form-control'),
		$indeterminateCheckbox = $('[data-toggle="indeterminate"]');


	// Methods

	function init($this) {
		$this.on('focus blur', function(e) {
        	$(this).parents('.form-group').toggleClass('focused', (e.type === 'focus'));
    	}).trigger('blur');
	}


	// Events

	if ($input.length) {
		init($input);
	}

	// Add indeterminate state to a checkbox
	if($indeterminateCheckbox.length) {
		$indeterminateCheckbox.each(function() {
			$(this).prop('indeterminate', true)
		})
	}

})();


//
// Custom input file
//

var CustomInputFile = (function() {

	// Variables

	var $customInputFile = $('.custom-input-file');


	// Methods

	function change($input, $this, $e) {
		var fileName,
			$label = $input.next('label'),
			labelVal = $label.html();

		if ($this && $this.files.length > 1) {
			fileName = ($this.getAttribute('data-multiple-caption') || '').replace('{count}', $this.files.length);
		}
		else if ($e.target.value) {
			fileName = $e.target.value.split('\\').pop();
		}

		if (fileName) {
			$label.find('span').html(fileName);
		}
		else {
			$label.html(labelVal);
		}
	}

	function focus($input) {
		$input.addClass('has-focus');
	}

	function blur($input) {
		$input.removeClass('has-focus');
	}


	// Events

	if ($customInputFile.length) {
		$customInputFile.each(function() {
			var $input = $(this);

			$input.on('change', function(e) {
				var $this = this,
					$e = e;

				change($input, $this, $e);
	        });

	        // Firefox bug fix
	        $input.on('focus', function() {
	            focus($input);
	        })
	        .on('blur', function() {
	            blur($input);
	        });
		});
	}
})();

//
// Sticky Navbar
//

var NavbarSticky = (function() {

	// Variables

	var $nav = $('.navbar-sticky'),
        navOffsetTop = 0,
		scrolling = false;


	// Methods

	function init($this) {

		// our current vertical position from the top
		var scrollTop = $(window).scrollTop(),
			navHeight = $this.outerHeight();

		if (scrollTop > (navOffsetTop + 200)) {
			$this.addClass('sticky');
			$("body").css("padding-top", navHeight + "px");
		} else {
			$this.removeClass('sticky');
			$("body").css("padding-top", "0");
		}
	}


	// Events

	if ($nav.length) {

		navOffsetTop = $nav.offset().top;
		
		$(window).on({
			'scroll': function() {
				scrolling = true;

				setInterval(function() {
					if (scrolling) {
						scrolling = false;

						// Sticky navbar init
                        init($nav);
					}
				}, 250);
			}
		})
	}
})();

//
// Toggle password visibility
//

'use strict';

var PasswordText = (function() {

	//
	// Variables
	//

	var $trigger = $('[data-toggle="password-text"]');


	//
	// Methods
	//

	function init($this) {
		var $password = $($this.data('target'));

		$password.attr('type') == 'password' ? $password.attr('type', 'text') : $password.attr('type', 'password');

		return false;
	}


	//
	// Events
	//

	if ($trigger.length) {
		// Init scroll on click
		$trigger.on('click', function(event) {
			init($(this));
		});
	}

})();

//
// Pricing
//

'use strict';


var Pricing = (function() {

	// Variables

	var $pricingContainer = $('.pricing-container'),
		$btn = $('.pricing-container button[data-pricing]');


	// Methods

	function init($this) {
        var a = $this.data('pricing'),
            b = $this.parents('.pricing-container'),
            c = $('.'+b.attr('class')+' [data-pricing-value]');


        if(!$this.hasClass('active')) {
            // Toggle active classes for monthly/yearly buttons
            $('.'+b.attr('class')+' button[data-pricing]').removeClass('active');
            $this.addClass('active');

            // Change price values
            c.each(function() {
                var new_val = $(this).data('pricing-value');
                var old_val = $(this).find('span.price').text();

                $(this).find('span.price').text(new_val);
                $(this).data('pricing-value', old_val);
            });
        }
	}


	// Events

	if ($pricingContainer.length) {
		$btn.on({
    		'click': function() {
    			init($(this));
    		}
    	})
	}

})();

//
// Scroll to (anchor links)
//

'use strict';

var ScrollTo = (function() {

	//
	// Variables
	//

	var $scrollTo = $('.scroll-me, [data-scroll-to], .toc-entry a'),
		urlHash = window.location.hash;


	//
	// Methods
	//

	function init(hash) {
		$('html, body').animate({
	        scrollTop: $(hash).offset().top
	    }, 'slow');
	}

	function scrollTo($this) {
		var $el = $this.attr('href');
        var offset = $this.data('scroll-to-offset') ? $this.data('scroll-to-offset') : 0;
		var options = {
			scrollTop: $($el).offset().top - offset
		};

        // Animate scroll to the selected section
        $('html, body').stop(true, true).animate(options, 300);

        event.preventDefault();
	}


	//
	// Events
	//

	if ($scrollTo.length) {
		// Init scroll on click
		$scrollTo.on('click', function(event) {
			scrollTo($(this));
		});
	}

	$(window).on("load", function () {
		// Init scroll on page load if a hash is present
		if(urlHash && urlHash != '#!' && $(urlHash).length) {
			init(urlHash)
		}
	});
})();

//
// Google maps
//

var GoogleMapCustom = (function() {
    var $map = document.getElementById('map-custom'),
        lat,
        lng,
        color,
        zoom;

    function initMap(map) {

        lat = map.getAttribute('data-lat');
        lng = map.getAttribute('data-lng');
        color = map.getAttribute('data-color');
        zoom = map.getAttribute('data-zoom') ? parseInt(map.getAttribute('data-zoom')) : 12;

        var myLatlng = new google.maps.LatLng(lat, lng);

        var mapOptions = {
            zoom: zoom,
            scrollwheel: false,
            center: myLatlng,
            mapTypeId: google.maps.MapTypeId.ROADMAP,
            styles: [{"featureType":"administrative","elementType":"labels.text.fill","stylers":[{"color":"#444444"}]},{"featureType":"landscape","elementType":"all","stylers":[{"color":"#f2f2f2"}]},{"featureType":"poi","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"road","elementType":"all","stylers":[{"saturation":-100},{"lightness":45}]},{"featureType":"road.highway","elementType":"all","stylers":[{"visibility":"simplified"}]},{"featureType":"road.arterial","elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"transit","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"water","elementType":"all","stylers":[{"color":color},{"visibility":"on"}]}]
        }

        map = new google.maps.Map(map, mapOptions);

        var marker = new google.maps.Marker({
            position: myLatlng,
            map: map,
            animation: google.maps.Animation.DROP,
            title: 'Hello World!'
        });

        var contentString = '<div class="info-window-content"><h5>Company Name</h5>' +
            '<p>Description comes here...</p></div>';

        var infowindow = new google.maps.InfoWindow({
            content: contentString
        });

        google.maps.event.addListener(marker, 'click', function() {
            infowindow.open(map, marker);
        });
    }

    if (typeof($map) != 'undefined' && $map != null) {
        google.maps.event.addDomListener(window, 'load', initMap($map));
    }
})();

//
// Google maps for MM
//

var GoogleMapCustom = (function() {
    var $map = document.getElementById('map-mm-dormitory'),
        lat_mm,
        lng_mm,
        lat_d,
        lng_d,
        color,
        zoom;

    function initMap(map) {

        // Faculty of Mathematics and Mechanics
        lat_mm = 59.87996;
        lng_mm = 29.8305919;

        // Dormitory
        lat_d = 59.87487;
        lng_d = 29.8248978;

        color = map.getAttribute('data-color');
        zoom = map.getAttribute('data-zoom') ? parseInt(map.getAttribute('data-zoom')) : 12;

        var myLatlng_mm = new google.maps.LatLng(lat_mm, lng_mm);
        var myLatlng_d = new google.maps.LatLng(lat_d, lng_d);

        var mapOptions = {
            zoom: zoom,
            scrollwheel: false,
            center: myLatlng_mm,
            mapTypeId: google.maps.MapTypeId.ROADMAP,
            styles: [{"featureType":"administrative","elementType":"labels.text.fill","stylers":[{"color":"#444444"}]},{"featureType":"landscape","elementType":"all","stylers":[{"color":"#f2f2f2"}]},{"featureType":"poi","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"road","elementType":"all","stylers":[{"saturation":-100},{"lightness":45}]},{"featureType":"road.highway","elementType":"all","stylers":[{"visibility":"simplified"}]},{"featureType":"road.arterial","elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"transit","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"water","elementType":"all","stylers":[{"color":color},{"visibility":"on"}]}]
        }

        map = new google.maps.Map(map, mapOptions);

        var marker_mm = new google.maps.Marker({
            position: myLatlng_mm,
            map: map,
            animation: google.maps.Animation.DROP,
            title: 'Математико-механической факультет'
        });

        var marker_d = new google.maps.Marker({
            position: myLatlng_d,
            map: map,
            animation: google.maps.Animation.DROP,
            title: 'Петергофский кампус СПбГУ'
        });

        var contentString_mm = '<div class="info-window-content"><h5>Математико-Механический факультет, СПбГУ</h5>' +
            '<p>Учебный корпус математико-механического факультета, СПбГУ</p></div>';

        var contentString_d = '<div class="info-window-content"><h5>Петергофский кампус СПбГУ</h5>' +
            '<p>Общежитие, СПбГУ</p></div>';

        var infowindow_mm = new google.maps.InfoWindow({
            content: contentString_mm
        });

        var infowindow_d = new google.maps.InfoWindow({
            content: contentString_d
        });

        google.maps.event.addListener(marker_mm, 'click', function() {
            infowindow_mm.open(map, marker_mm);
        });
        google.maps.event.addListener(marker_d, 'click', function() {
            infowindow_d.open(map, marker_d);
        });
    }

    if (typeof($map) != 'undefined' && $map != null) {
        google.maps.event.addDomListener(window, 'load', initMap($map));
    }
})();
//
// Google maps
//

var GoogleMap = (function() {
    var $map = document.getElementById('map-default'),
        lat,
        lng,
        zoom;

    function initMap(map) {

        lat = map.getAttribute('data-lat');
        lng = map.getAttribute('data-lng');
        zoom = map.getAttribute('data-zoom') ? parseInt(map.getAttribute('data-zoom')) : 12;

        var myLatlng = new google.maps.LatLng(lat, lng);

        var mapOptions = {
            zoom: zoom,
            scrollwheel: false,
            center: myLatlng,
            mapTypeId: google.maps.MapTypeId.ROADMAP,
        }

        map = new google.maps.Map(map, mapOptions);

        var marker = new google.maps.Marker({
            position: myLatlng,
            map: map,
            animation: google.maps.Animation.DROP,
            title: 'Hello World!'
        });

        var contentString = '<div class="info-window-content"><h2>{{ site.product.name }} {{ site.product.name_long }}</h2>' +
            '<p>{{ site.product.description }}</p></div>';

        var infowindow = new google.maps.InfoWindow({
            content: contentString
        });

        google.maps.event.addListener(marker, 'click', function() {
            infowindow.open(map, marker);
        });
    }

    if (typeof($map) != 'undefined' && $map != null) {
        google.maps.event.addDomListener(window, 'load', initMap($map));
    }
})();

//
// Autosize
// used on textarea inputs
//

'use strict';

var TextareaAutosize = (function() {

	//
	// Variables
	//

	var $textarea = $('[data-toggle="autosize"]');

	//
	// Functions
	//

	function init() {
		autosize($textarea);
	}

	//
	// Events
	//

	if ($textarea.length) {
		init();
	}

})();

//
// Countdown
//

'use strict';

var Countdown = (function() {

	//
	// Variables
	//

	var $countdown = $('.countdown');

	//
	// Functions
	//

	function init($this) {
		var date = $this.data('countdown-date'),
			template = '<div class="countdown-item"><span class="countdown-digit">%-D</span><span class="countdown-label countdown-days">day%!D</span></div>' +
			'<div class="countdown-item"><span class="countdown-digit">%H</span><span class="countdown-separator">:</span><span class="countdown-label">hrs</span></div>' +
			'<div class="countdown-item"><span class="countdown-digit">%M</span><span class="countdown-separator">:</span><span class="countdown-label">min</span></div>' +
			'<div class="countdown-item"><span class="countdown-digit">%S</span><span class="countdown-label">sec</span></div>';

		$this.countdown(date).on('update.countdown', function(event) {
			var $this = $(this).html(event.strftime('' + template));
		});
	}

	//
	// Events
	//

	if ($countdown.length) {
		$countdown.each(function() {
			init($(this));
		})
	}

})();

//
// Counter
//

'use strict';

! function(t) {
	t.fn.countTo = function(e) {
		return e = e || {}, t(this).each(function() {
			var a = t.extend({}, t.fn.countTo.defaults, {
					from: t(this).data("from"),
					to: t(this).data("to"),
					speed: t(this).data("speed"),
					refreshInterval: t(this).data("refresh-interval"),
					decimals: t(this).data("decimals")
				}, e),
				n = Math.ceil(a.speed / a.refreshInterval),
				o = (a.to - a.from) / n,
				r = this,
				l = t(this),
				f = 0,
				i = a.from,
				c = l.data("countTo") || {};

			function s(t) {
				var e = a.formatter.call(r, t, a);
				l.text(e)
			}
			l.data("countTo", c), c.interval && clearInterval(c.interval), c.interval = setInterval(function() {
				f++, s(i += o), "function" == typeof a.onUpdate && a.onUpdate.call(r, i);
				f >= n && (l.removeData("countTo"), clearInterval(c.interval), i = a.to, "function" == typeof a.onComplete && a.onComplete.call(r, i))
			}, a.refreshInterval), s(i)
		})
	}, t.fn.countTo.defaults = {
		from: 0,
		to: 0,
		speed: 1e3,
		refreshInterval: 100,
		decimals: 0,
		formatter: function(t, e) {
			return t.toFixed(e.decimals)
		},
		onUpdate: null,
		onComplete: null
	}
}(jQuery);


var Counter = (function() {

	// Variables

	var counter = '.counter',
		$counter = $(counter);


	// Methods

	function init($this) {
		inView(counter)
		.on('enter', function() {
			if(! $this.hasClass('counting-finished')) {
				$this.countTo({
					formatter: function(value, options) {
						return value.toFixed(options.decimals);
					},
					onUpdate: function(value) {
						//console.debug(this);
					},
					onComplete: function(value) {
						$(this).addClass('counting-finished');
					}
				});
			}
		})
	}


	// // Events

	if ($counter.length) {
		init($counter);
	}

})();

//
// Datepicker
//

'use strict';

var Datepicker = (function() {

	//
	// Variables
	//

	var $date = $('[data-toggle="date"]'),
		$datetime = $('[data-toggle="datetime"]'),
		$time = $('[data-toggle="time"]');


	//
	// Methods
	//

	function initDate($this) {

		var options = {
			enableTime: false,
			allowInput: true
		};

		$this.flatpickr(options);
	}

	function initDatetime($this) {

		var options = {
			enableTime: true,
			allowInput: true
		};

		$this.flatpickr(options);
	}

	function initTime($this) {

		var options = {
			noCalendar: true,
            enableTime: true,
			allowInput: true
		};

		$this.flatpickr(options);
	}


	//
	// Events
	//

	if ($date.length) {

		// Init selects
		$date.each(function() {
			initDate($(this));
		});
	}

	if ($datetime.length) {

		// Init selects
		$datetime.each(function() {
			initDatetime($(this));
		});
	}

	if ($time.length) {

		// Init selects
		$time.each(function() {
			initTime($(this));
		});
	}

})();

//
// Highlight.js
//

'use strict';

var Highlight = (function() {

	//
	// Variables
	//

	var $highlight = $('.highlight');


	//
	// Methods
	//

	function init(i, block) {
		// Insert the copy button inside the highlight block
		var btnHtml = '<button class="action-item btn-clipboard" title="Copy to clipboard"><i data-feather="copy"></i></button>'
		$(block).before(btnHtml)
		$('.btn-clipboard')
			.tooltip()
			.on('mouseleave', function() {
				// Explicitly hide tooltip, since after clicking it remains
				// focused (as it's a button), so tooltip would otherwise
				// remain visible until focus is moved away
				$(this).tooltip('hide');
			});

		// Component code copy/paste
		var clipboard = new ClipboardJS('.btn-clipboard', {
			target: function(trigger) {
				return trigger.nextElementSibling
			}
		})

		clipboard.on('success', function(e) {
			$(e.trigger)
				.attr('title', 'Copied!')
				.tooltip('_fixTitle')
				.tooltip('show')
				.attr('title', 'Copy to clipboard')
				.tooltip('_fixTitle')

			e.clearSelection()
		})

		clipboard.on('error', function(e) {
			var modifierKey = /Mac/i.test(navigator.userAgent) ? '\u2318' : 'Ctrl-'
			var fallbackMsg = 'Press ' + modifierKey + 'C to copy'

			$(e.trigger)
				.attr('title', fallbackMsg)
				.tooltip('_fixTitle')
				.tooltip('show')
				.attr('title', 'Copy to clipboard')
				.tooltip('_fixTitle')
		})

		// Initialize highlight.js plugin
		hljs.highlightBlock(block);
	}


	//
	// Events
	//

	$highlight.each(function(i, block) {
		init(i, block);
	});

})();

//
// Isotope - Masonry Layout
//

'use strict';

var Masonry = (function() {

	// Variables

	var $masonryContainer = $(".masonry-container");


	// Methods

	function init($this) {
		var $el = $this.find('.masonry'),
			$filters = $this.find('.masonry-filter-menu'),
			$defaultFilter = $filters.find('.active'),
			defaultFilterValue = $defaultFilter.data('filter');

		var $masonry = $el.imagesLoaded(function() {

			// Set default filter if exists

			if (defaultFilterValue != undefined && defaultFilterValue != '') {

				if (defaultFilterValue != '*') {
					defaultFilterValue = '.' + defaultFilterValue;
				}

				$defaultFilter.addClass('active');
			}


			// Plugin options
			var options = {
				itemSelector: '.masonry-item',
				filter: defaultFilterValue
			};

			// Init plugin
			$masonry.isotope(options);
		});


		// Sorting buttons (filters)

        $filters.on('click', 'a', function(e) {
			e.preventDefault();

			var $this = $(this),
             	val = $(this).attr('data-filter');

            if (val == '*') {
                val = '';
            } else {
                val = '.' + val;
            }

            $masonry.isotope({
                filter: val
            }).on( 'arrangeComplete', function() {
				$filters.find('[data-filter]').removeClass('active');
				$this.addClass('active');
			} );
        });

	}


	// Events

	if ($masonryContainer.length) {
		$masonryContainer.each(function() {
			init($(this));
		})
	}

})();

//
// Notify
// init of the bootstrap-notify plugin
//

'use strict';

var Notify = (function() {

	// Variables

	var $notifyBtn = $('[data-toggle="notify"]');


	// Methods

	function notify(placement, align, icon, type, animIn, animOut) {
		$.notify({
			icon: icon,
			title: ' Bootstrap Notify',
			message: 'Turning standard Bootstrap alerts into awesome notifications',
			url: ''
		}, {
			element: 'body',
			type: type,
			allow_dismiss: true,
			placement: {
				from: placement,
				align: align
			},
			offset: {
				x: 15, // Keep this as default
				y: 15 // Unless there'll be alignment issues as this value is targeted in CSS
			},
			spacing: 10,
			z_index: 1080,
			delay: 2500,
			timer: 25000,
			url_target: '_blank',
			mouse_over: false,
			animate: {
				// enter: animIn,
				// exit: animOut
                enter: animIn,
                exit: animOut
			},
			template:   '<div class="alert alert-{0} alert-icon alert-group alert-notify" data-notify="container" role="alert">' +
					  		'<div class="alert-group-prepend align-self-start">' +
					  			'<span class="alert-group-icon"><i data-notify="icon"></i></span>' +
					  		'</div>' +
					  		'<div class="alert-content">' +
								'<strong data-notify="title">{1}</strong>' +
								'<div data-notify="message">{2}</div>' +
							'</div>' +
					  		'<button type="button" class="close" data-notify="dismiss" aria-label="Close">' +
								'<span aria-hidden="true">&times;</span>' +
							'</button>' +
						'</div>'

		});
	}

	// Events

	if ($notifyBtn.length) {
		$notifyBtn.on('click', function(e) {
			e.preventDefault();

			var placement = $(this).attr('data-placement');
			var align = $(this).attr('data-align');
			var icon = $(this).attr('data-icon');
			var type = $(this).attr('data-type');
			var animIn = $(this).attr('data-animation-in');
			var animOut = $(this).attr('data-animation-out');

			notify(placement, align, icon, type, animIn, animOut);
		})
	}

})();

//
// Popover
//

'use strict';

var ProgressCircle = (function() {

	// Variables

	var $progress = $('.progress-circle');

	// Methods

	function init($this) {

        var value = $this.data().progress,
			text = $this.data().text ? $this.data().text : '',
			textClass = $this.data().textclass ? $this.data().textclass : 'progressbar-text',
            color = $this.data().color ? $this.data().color : 'primary',
			trailWidth = $this.data().trailwidth ? $this.data().trailwidth : 2,
			shape = $this.data().shape ? $this.data().shape : 'circle'

		var options = {
			color: PurposeStyle.colors.theme[color],
			strokeWidth: 7,
			trailWidth: trailWidth,
			text: {
				value: text,
				className: textClass
			},
            svgStyle: {
                display: 'block',
            },
            duration: 1500,
            easing: 'easeInOut'
		};

		if (shape == 'circle') {
			var progress = new ProgressBar.Circle($this[0], options);
		}
		else if (shape == 'semi-circle') {
			var progress = new ProgressBar.SemiCircle($this[0], options);
		}


        progress.animate(value / 100);
	}


	// Events

	if ($progress.length) {
		$progress.each(function() {
			init($(this));
		});
	}

})();

//
// Select2
//

'use strict';

var Select = (function() {

	var $select = $('[data-toggle="select"]');

	function init($this) {
		var options = {};

		$this.select2(options);
	}

	if ($select.length) {
		$select.each(function() {
			init($(this));
		});
	}

})();

//
// Sticky
//

'use strict';

var Sticky = (function() {

	//
	// Variables
	//

	var $sticky = $('[data-toggle="sticky"]');


	//
	// Methods
	//

	function init($this) {

		var offset = $this.data('sticky-offset') ? $this.data('sticky-offset') : 0;
		var options = {
			'offset_top': offset
		};

		if($(window).width() > 1000) {
			$this.stick_in_parent(options);
		} else {
			$this.trigger("sticky_kit:detach");
		}
	}


	//
	// Events
	//

	$(window).on('load resize', function() {
		if ($sticky.length) {

			// Init selects
			$sticky.each(function() {
				init($(this));
			});
		}
	})


})();

//
// Swiper
// init of plugin Swiper JS
//

'use strict';

var WpxSwiper = (function() {

	// Variables

	var $swiperContainer = $(".swiper-js-container"),
	 	animEndEv = 'webkitAnimationEnd animationend';


	// Methods

	function init($this) {

		// Swiper elements

        var $el = $this.find('.swiper-container'),
			pagination = $this.find('.swiper-pagination'),
			navNext = $this.find('.swiper-button-next'),
			navPrev = $this.find('.swiper-button-prev');


		// Swiper options

        var effect = $el.data('swiper-effect') ? $el.data('swiper-effect') : 'slide',
        	direction = $el.data('swiper-direction') ? $el.data('swiper-direction') :  'horizontal',
			initialSlide = $el.data('swiper-initial-slide') ? $el.data('swiper-initial-slide') : 0,
			autoHeight = $el.data('swiper-autoheight') ? $el.data('swiper-autoheight') : false,
			autoplay = $el.data('swiper-autoplay') ? $el.data('swiper-autoplay') : false,
			centeredSlides = $el.data('swiper-centered-slides') ? $el.data('swiper-centered-slides') : false,
			paginationType = $el.data('swiper-pagination-type') ? $el.data('swiper-pagination-type') : 'bullets';



		// Items per slide

        var items = $el.data('swiper-items');
        var itemsSm = $el.data('swiper-sm-items');
        var itemsMd = $el.data('swiper-md-items');
        var itemsLg = $el.data('swiper-lg-items');
		var itemsXl = $el.data('swiper-xl-items');


		// Space between items

        var spaceBetween = $el.data('swiper-space-between');
        var spaceBetweenSm = $el.data('swiper-sm-space-between');
        var spaceBetweenMd = $el.data('swiper-md-space-between');
        var spaceBetweenLg = $el.data('swiper-lg-space-between');
		var spaceBetweenXl = $el.data('swiper-xl-space-between');


		// Slides per view written in data attributes for adaptive resoutions

        items = items ? items : 1;
        itemsSm = itemsSm ? itemsSm : items;
		itemsMd = itemsMd ? itemsMd : itemsSm;
        itemsLg = itemsLg ? itemsLg : itemsMd;
        itemsXl = itemsXl ? itemsXl : itemsLg;


        // Space between slides written in data attributes for adaptive resoutions

        spaceBetween = !spaceBetween ? 0 : spaceBetween;
        spaceBetweenSm = !spaceBetweenSm ? spaceBetween : spaceBetweenSm;
        spaceBetweenMd = !spaceBetweenMd ? spaceBetweenSm : spaceBetweenMd;
        spaceBetweenLg = !spaceBetweenLg ? spaceBetweenMd : spaceBetweenLg;
		spaceBetweenXl = !spaceBetweenXl ? spaceBetweenLg : spaceBetweenXl;

		var $swiper = new Swiper($el, {
            pagination: {
                el: pagination,
                clickable: true,
				type: paginationType
            },
            navigation: {
                nextEl: navNext,
                prevEl: navPrev,
            },
            slidesPerView: items,
            spaceBetween: spaceBetween,
            initialSlide: initialSlide,
            autoHeight: autoHeight,
            centeredSlides: centeredSlides,
            mousewheel: false,
			keyboard: {
			    enabled: true,
			    onlyInViewport: false,
			},
            grabCursor: true,
			autoplay: autoplay,
            effect: effect,
            coverflowEffect: {
                rotate: 0,
                stretch: 0,
                depth: 50,
                modifier: 3,
                slideShadows: false
            },
            speed: 800,
            direction: direction,
            preventClicks: true,
            preventClicksPropagation: true,
            observer: true,
            observeParents: true,
			breakpointsInverse: true,
			breakpoints: {
                575: {
                    slidesPerView: itemsSm,
                    spaceBetween: spaceBetweenSm
                },
                767: {
                    slidesPerView: itemsMd,
                    spaceBetween: spaceBetweenMd
                },
                991: {
                    slidesPerView: itemsLg,
                    spaceBetween: spaceBetweenLg
                },
                1199: {
                    slidesPerView: itemsXl,
                    spaceBetween: spaceBetweenXl
                }
            }
        });
	}


	// Events
	$(document).ready(function() {
		if ($swiperContainer.length) {
			$swiperContainer.each(function(i, swiperContainer) {
				init($(swiperContainer));
			})
		}
	})

})();

//
// Tags input
//

'use strict';

var Tags = (function() {

	//
	// Variables
	//

	var $tags = $('[data-toggle="tags"]');


	//
	// Methods
	//

	function init($this) {

		var options = {
			tagClass: 'badge badge-primary'
		};

		$this.tagsinput(options);
	}


	//
	// Events
	//

	if ($tags.length) {

		// Init selects
		$tags.each(function() {
			init($(this));
		});
	}

})();

//
// Typed
// text typing animation
//

'use strict';

var Typed = (function() {

	// Variables

	var typed = '.typed',
		$typed = $(typed);


	// Methods

	function init($this) {
		var el = '#' + $this.attr('id'),
        	strings = $this.data('type-this'),
			strings = strings.split(',');

		var options = {
			strings: strings,
            typeSpeed: 100,
            backSpeed: 70,
            loop: true
		};

        var animation = new Typed(el, options);

		inView(el).on('enter', function() {
			animation.start();
		}).on('exit', function() {
			animation.stop();
		});
	}


	// Events

	if ($typed.length) {
		$typed.each(function() {
			init($(this));
		});
	}

})();

//
// Engagement chart
//

'use strict';

var ApexOrdersChart = (function() {

	// Variables

	var $chart = document.querySelector("#apex-orders"),
		$legendItem = $('.legend input'),
		chart;

	var colorPalette = [
		PurposeStyle.colors.theme['primary'],
		PurposeStyle.colors.theme['warning']
	]

	function init() {
		var options = {
			chart: {
				type: 'bar',
				stacked: false,
				zoom: {
					enabled: false
				},
				toolbar: {
					show: false
				},
				shadow: {
					enabled: false,
				},
				animations: {
			        enabled: true,
			        easing: 'easeinout',
			        speed: 800,
			        animateGradually: {
			            enabled: true,
			            delay: 150
			        },
			        dynamicAnimation: {
			            enabled: true,
			            speed: 350
			        }
			    }
			},
			colors: colorPalette,
			plotOptions: {
				bar: {
					columnWidth: '20%',
					endingShape: 'rounded'
				}
			},
			stroke: {
				width: 0,
				curve: 'smooth'
			},
			series: [{
				name: 'Delivered',
				type: 'bar',
				data: [50, 30, 40, 60, 80, 100, 90, 90, 70, 90, 100]
			}, {
				name: 'Rejected',
				type: 'bar',
				data: [15, 20, 20, 15, 15, 30, 20, 15, 30, 20, 30]
			}],
			markers: {
				size: 0
			},
			xaxis: {
				axisBorder: {
					show: false
				},
				axisTicks: {
					show: false
				},
				categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
				labels: {
					style: {
						colors: PurposeStyle.colors.gray[500],
						fontSize: '13px',
						fontFamily: PurposeStyle.fonts.base,
						cssClass: 'apexcharts-xaxis-label',
					}
				}
			},
			yaxis: {
				axisBorder: {
					show: false
				},
				axisTicks: {
					show: false
				},
				labels: {
					style: {
						color: PurposeStyle.colors.gray[500],
						fontSize: '13px',
						fontFamily: PurposeStyle.fonts.base,
						cssClass: 'apexcharts-xaxis-label',
					}
				}
			},
			legend: {
				show: false
			},
			grid: {
				borderColor: PurposeStyle.colors.gray[200],
				strokeDashArray: 3,
			},
			dataLabels: {
				enabled: false
			},
			tooltip: {
				shared: true,
				intersect: false,
				y: {
					formatter: function(y) {
						if (typeof y !== "undefined") {
							return y.toFixed(0) + " orders";
						}
						return y;
					}
				}
			}
		}

		// Get data from data attributes
		var height = $chart.dataset.height;

		// Inject synamic properties
		options.colors = colorPalette;

		options.chart.height = height ? height : 350;

		chart = new ApexCharts($chart, options);

		// Draw chart
		setTimeout(function() {
			chart.render();

			checkLegends()
		}, 300);
	}


	// check if the checkbox has any unchecked item
	// checkLegends()

	function checkLegends() {
		var allLegends = document.querySelectorAll(".legend input[type='checkbox']")

		for (var i = 0; i < allLegends.length; i++) {
			if (!allLegends[i].checked) {
				chart.toggleSeries(allLegends[i].value)
			}
		}
	}

	// toggleSeries accepts a single argument which should match the series name you're trying to toggle
	function toggleSeries(checkbox) {
		chart.toggleSeries(checkbox.value)
	}

	if ($chart) {
		init();

		return {
			toggleSeries: toggleSeries
		};
	}

})();

//
// Engagement chart
//

'use strict';

var ApexTasksChart = (function() {

	// Variables

	var $chart = document.querySelector("#apex-tasks"),
		$legendItem = $('.legend input'),
		chart;

	var colorPalette = [
		PurposeStyle.colors.theme['primary'],
		PurposeStyle.colors.theme['warning']
	]

	function init() {
		var options = {
			chart: {
				type: 'bar',
				stacked: true,
				zoom: {
					enabled: false
				},
				toolbar: {
					show: false
				},
				shadow: {
					enabled: false,
				},
				animations: {
			        enabled: true,
			        easing: 'easeinout',
			        speed: 800,
			        animateGradually: {
			            enabled: true,
			            delay: 150
			        },
			        dynamicAnimation: {
			            enabled: true,
			            speed: 350
			        }
			    }
			},
			colors: colorPalette,
			plotOptions: {
				bar: {
					columnWidth: '20%',
					endingShape: 'rounded'
				}
			},
			stroke: {
				width: 0,
				curve: 'smooth'
			},
			series: [{
				name: 'Finished',
				type: 'bar',
				data: [50, 30, 40, 60, 80, 100, 90, 90, 70, 90, 100]
			}, {
				name: 'Unfinished',
				type: 'bar',
				data: [15, 20, 20, 15, 15, 30, 20, 15, 30, 20, 30]
			}],
			markers: {
				size: 0
			},
			xaxis: {
				axisBorder: {
					show: false
				},
				axisTicks: {
					show: false
				},
				categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
				labels: {
					style: {
						colors: PurposeStyle.colors.gray[500],
						fontSize: '13px',
						fontFamily: PurposeStyle.fonts.base,
						cssClass: 'apexcharts-xaxis-label',
					}
				}
			},
			yaxis: {
				axisBorder: {
					show: false
				},
				axisTicks: {
					show: false
				},
				labels: {
					style: {
						color: PurposeStyle.colors.gray[500],
						fontSize: '13px',
						fontFamily: PurposeStyle.fonts.base,
						cssClass: 'apexcharts-xaxis-label',
					}
				}
			},
			legend: {
				show: false
			},
			grid: {
				borderColor: PurposeStyle.colors.gray[200],
				strokeDashArray: 3,
			},
			dataLabels: {
				enabled: false
			},
			tooltip: {
				shared: true,
				intersect: false,
				y: {
					formatter: function(y) {
						if (typeof y !== "undefined") {
							return y.toFixed(0) + " tasks";
						}
						return y;

					}
				}
			}
		}

		// Get data from data attributes
		var height = $chart.dataset.height;

		// Inject synamic properties
		options.colors = colorPalette;

		options.chart.height = height ? height : 350;

		chart = new ApexCharts($chart, options);

		// Draw chart
		setTimeout(function() {
			chart.render();
		}, 300);
	}

	if ($chart) {
		init();
	}

})();

//# sourceMappingURL=quick-website.js.map
