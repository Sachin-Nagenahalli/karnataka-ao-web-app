/**
 * Karnataka AO Last-Minute Revision Handbook - Main JS Script
 * Frontend security controls and handbook reader implementation
 */

document.addEventListener('DOMContentLoaded', () => {
    // ----------------------------------------------------------------
    // 1. Copy-Protection Controls (Global)
    // ----------------------------------------------------------------
    
    // Disable Right-Click Context Menu
    document.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        return false;
    });

    // Disable Text Copying
    document.addEventListener('copy', (e) => {
        e.preventDefault();
        alert('Copying contents of this handbook is strictly prohibited.');
        return false;
    });

    // Disable Common Keyboard Shortcuts (Save, Print, View Source, DevTools)
    document.addEventListener('keydown', (e) => {
        const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
        
        // Command/Control key
        const cmdCtrl = isMac ? e.metaKey : e.ctrlKey;
        
        // Block Save (Ctrl+S / Cmd+S)
        if (cmdCtrl && e.key.toLowerCase() === 's') {
            e.preventDefault();
            alert('Saving this handbook offline is disabled.');
            return false;
        }

        // Block Print (Ctrl+P / Cmd+P)
        if (cmdCtrl && e.key.toLowerCase() === 'p') {
            e.preventDefault();
            alert('Printing this handbook is disabled.');
            return false;
        }

        // Block View Source (Ctrl+U / Cmd+Option+U)
        if (cmdCtrl && e.key.toLowerCase() === 'u') {
            e.preventDefault();
            return false;
        }

        // Block Inspect Element shortcuts (F12, Ctrl+Shift+I, Cmd+Option+I)
        if (e.key === 'F12' || 
            (cmdCtrl && e.shiftKey && e.key.toLowerCase() === 'i') || 
            (isMac && cmdCtrl && e.altKey && e.key.toLowerCase() === 'i')) {
            e.preventDefault();
            return false;
        }
    });

    // Prevent drag and drop on images
    document.addEventListener('dragstart', (e) => {
        if (e.target.nodeName === 'IMG') {
            e.preventDefault();
            return false;
        }
    });

    // ----------------------------------------------------------------
    // 2. Registration Form Validation
    // ----------------------------------------------------------------
    const regForm = document.getElementById('registrationForm');
    if (regForm) {
        regForm.addEventListener('submit', (e) => {
            let isValid = true;
            
            const mobileInput = document.getElementById('mobile');
            const mobileError = document.getElementById('mobileError');
            const mobileVal = mobileInput.value.trim();
            
            // Clean mobile inputs and check for 10 digits
            const digitsOnly = mobileVal.replace(/\D/g, '');
            if (digitsOnly.length !== 10) {
                mobileError.textContent = 'Please enter a valid 10-digit mobile number.';
                mobileError.style.display = 'block';
                isValid = false;
            } else {
                mobileError.style.display = 'none';
                mobileInput.value = digitsOnly; // Submit clean digits
            }
            
            const nameInput = document.getElementById('name');
            const nameError = document.getElementById('nameError');
            if (nameInput.value.trim().length < 3) {
                nameError.textContent = 'Name must be at least 3 characters long.';
                nameError.style.display = 'block';
                isValid = false;
            } else {
                nameError.style.display = 'none';
            }

            const collegeInput = document.getElementById('college');
            const collegeError = document.getElementById('collegeError');
            if (collegeInput.value.trim().length < 4) {
                collegeError.textContent = 'Please enter your full college/university name.';
                collegeError.style.display = 'block';
                isValid = false;
            } else {
                collegeError.style.display = 'none';
            }

            if (!isValid) {
                e.preventDefault();
            }
        });
    }

    // ----------------------------------------------------------------
    // 3. Document Viewer Logic
    // ----------------------------------------------------------------
    const viewerViewport = document.getElementById('viewerViewport');
    if (viewerViewport) {
        const pageImg = document.getElementById('pageImage');
        const prevBtn = document.getElementById('prevPageBtn');
        const nextBtn = document.getElementById('nextPageBtn');
        const zoomInBtn = document.getElementById('zoomInBtn');
        const zoomOutBtn = document.getElementById('zoomOutBtn');
        const zoomFitBtn = document.getElementById('zoomFitBtn');
        const pageNumInput = document.getElementById('pageNumInput');
        const totalPagesSpan = document.getElementById('totalPages');
        const loadingOverlay = document.getElementById('viewerLoading');
        
        let currentPage = 1;
        const totalPages = parseInt(totalPagesSpan.textContent, 10) || 1;
        let zoomPercent = 100;
        
        // Prefetch image cache to make navigation fast
        const imageCache = {};

        function showLoading() {
            loadingOverlay.style.opacity = '1';
            loadingOverlay.style.pointerEvents = 'all';
        }

        function hideLoading() {
            loadingOverlay.style.opacity = '0';
            loadingOverlay.style.pointerEvents = 'none';
        }

        function getPageUrl(pageNum) {
            return `/api/page/${pageNum}?t=${new Date().getTime()}`;
        }

        function loadPage(pageNum) {
            if (pageNum < 1 || pageNum > totalPages) return;
            
            showLoading();
            currentPage = pageNum;
            pageNumInput.value = currentPage;
            
            // Handle buttons disabled states
            prevBtn.disabled = (currentPage === 1);
            nextBtn.disabled = (currentPage === totalPages);
            
            const targetUrl = getPageUrl(currentPage);
            
            // Check if already in cache
            if (imageCache[currentPage]) {
                pageImg.src = imageCache[currentPage].src;
                hideLoading();
                prefetchNextPage();
            } else {
                const img = new Image();
                img.onload = () => {
                    pageImg.src = img.src;
                    imageCache[currentPage] = img; // cache it
                    hideLoading();
                    prefetchNextPage();
                };
                img.onerror = () => {
                    alert('Error loading page. Please refresh.');
                    hideLoading();
                };
                img.src = targetUrl;
            }
        }

        function prefetchNextPage() {
            const nextP = currentPage + 1;
            if (nextP <= totalPages && !imageCache[nextP]) {
                const img = new Image();
                img.onload = () => {
                    imageCache[nextP] = img;
                };
                img.src = getPageUrl(nextP);
            }
        }

        function updateZoom() {
            const wrapper = document.getElementById('pageWrapper');
            if (wrapper) {
                wrapper.style.width = `${zoomPercent}%`;
                wrapper.style.transform = `scale(1)`;
            }
        }

        // Viewport Event Listeners
        prevBtn.addEventListener('click', () => {
            if (currentPage > 1) {
                loadPage(currentPage - 1);
                viewerViewport.scrollTop = 0;
            }
        });

        nextBtn.addEventListener('click', () => {
            if (currentPage < totalPages) {
                loadPage(currentPage + 1);
                viewerViewport.scrollTop = 0;
            }
        });

        zoomInBtn.addEventListener('click', () => {
            if (zoomPercent < 200) {
                zoomPercent += 15;
                updateZoom();
            }
        });

        zoomOutBtn.addEventListener('click', () => {
            if (zoomPercent > 50) {
                zoomPercent -= 15;
                updateZoom();
            }
        });

        zoomFitBtn.addEventListener('click', () => {
            zoomPercent = 100;
            updateZoom();
            const wrapper = document.getElementById('pageWrapper');
            if (wrapper) {
                wrapper.style.width = '100%';
                wrapper.style.maxWidth = '800px';
            }
        });

        pageNumInput.addEventListener('change', () => {
            let val = parseInt(pageNumInput.value, 10);
            if (isNaN(val) || val < 1) val = 1;
            if (val > totalPages) val = totalPages;
            loadPage(val);
        });

        // Fullscreen Toggle functionality
        const fullscreenBtn = document.getElementById('fullscreenBtn');
        const viewerContainer = document.querySelector('.viewer-container');
        if (fullscreenBtn && viewerContainer) {
            fullscreenBtn.addEventListener('click', () => {
                if (!document.fullscreenElement && !document.webkitFullscreenElement) {
                    const req = viewerContainer.requestFullscreen || viewerContainer.webkitRequestFullscreen;
                    if (req) {
                        req.call(viewerContainer).then(() => {
                            fullscreenBtn.innerHTML = '<i class="fa-solid fa-compress"></i> Exit';
                        }).catch(err => {
                            console.error(`Error enabling fullscreen: ${err.message}`);
                        });
                    }
                } else {
                    const exit = document.exitFullscreen || document.webkitExitFullscreen;
                    if (exit) {
                        exit.call(document).then(() => {
                            fullscreenBtn.innerHTML = '<i class="fa-solid fa-expand"></i> Fullscreen';
                        });
                    }
                }
            });
            
            const onFullscreenChange = () => {
                const isFS = document.fullscreenElement || document.webkitFullscreenElement;
                if (!isFS) {
                    fullscreenBtn.innerHTML = '<i class="fa-solid fa-expand"></i> Fullscreen';
                }
            };
            document.addEventListener('fullscreenchange', onFullscreenChange);
            document.addEventListener('webkitfullscreenchange', onFullscreenChange);
        }

        // Add keyboard navigation (Left/Right Arrows)
        document.addEventListener('keydown', (e) => {
            if (document.activeElement.tagName === 'INPUT') return;
            
            if (e.key === 'ArrowRight') {
                nextBtn.click();
            } else if (e.key === 'ArrowLeft') {
                prevBtn.click();
            }
        });

        // Initialize the first page
        loadPage(1);
    }

    // ----------------------------------------------------------------
    // 4. Candidate Feedback Drawer Controls
    // ----------------------------------------------------------------
    const openFeedbackBtn = document.getElementById('openFeedbackBtn');
    const closeFeedbackBtn = document.getElementById('closeFeedbackBtn');
    const feedbackDrawer = document.getElementById('feedbackDrawer');
    const drawerOverlay = document.getElementById('drawerOverlay');
    const feedbackForm = document.getElementById('feedbackForm');
    const feedbackStatus = document.getElementById('feedbackStatus');
    const feedbackMessage = document.getElementById('feedbackMessage');
    const submitFeedbackBtn = document.getElementById('submitFeedbackBtn');

    if (openFeedbackBtn && feedbackDrawer && drawerOverlay) {
        // Toggle Open Drawer
        openFeedbackBtn.addEventListener('click', () => {
            feedbackDrawer.classList.add('open');
            drawerOverlay.classList.add('visible');
        });

        // Toggle Close Drawer
        const closeDrawer = () => {
            feedbackDrawer.classList.remove('open');
            drawerOverlay.classList.remove('visible');
            // Reset status
            feedbackStatus.style.display = 'none';
            feedbackStatus.textContent = '';
            feedbackStatus.className = 'feedback-status';
        };

        closeFeedbackBtn.addEventListener('click', closeDrawer);
        drawerOverlay.addEventListener('click', closeDrawer);

        // Submit Feedback Form via AJAX
        if (feedbackForm) {
            feedbackForm.addEventListener('submit', (e) => {
                e.preventDefault();
                
                const msg = feedbackMessage.value.trim();
                if (!msg) return;

                // Disable submit button during processing
                submitFeedbackBtn.disabled = true;
                submitFeedbackBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Submitting...';
                
                feedbackStatus.style.display = 'none';

                const formData = new FormData();
                formData.append('message', msg);

                fetch('/submit-feedback', {
                    method: 'POST',
                    body: formData
                })
                .then(res => res.json())
                .then(data => {
                    feedbackStatus.style.display = 'block';
                    if (data.status === 'success') {
                        feedbackStatus.textContent = data.message;
                        feedbackStatus.style.background = 'rgba(76, 175, 80, 0.15)';
                        feedbackStatus.style.border = '1px solid rgba(76, 175, 80, 0.3)';
                        feedbackStatus.style.color = '#a5d6a7';
                        
                        // Clear textarea
                        feedbackMessage.value = '';
                        
                        // Auto close drawer after 2.5 seconds
                        setTimeout(closeDrawer, 2500);
                    } else {
                        feedbackStatus.textContent = data.message || 'An error occurred. Please try again.';
                        feedbackStatus.style.background = 'rgba(239, 68, 68, 0.15)';
                        feedbackStatus.style.border = '1px solid rgba(239, 68, 68, 0.3)';
                        feedbackStatus.style.color = '#ef9a9a';
                    }
                })
                .catch(err => {
                    console.error('Error submitting feedback:', err);
                    feedbackStatus.style.display = 'block';
                    feedbackStatus.textContent = 'Network error occurred. Please check your connection.';
                    feedbackStatus.style.background = 'rgba(239, 68, 68, 0.15)';
                    feedbackStatus.style.border = '1px solid rgba(239, 68, 68, 0.3)';
                    feedbackStatus.style.color = '#ef9a9a';
                })
                .finally(() => {
                    submitFeedbackBtn.disabled = false;
                    submitFeedbackBtn.innerHTML = '<i class="fa-solid fa-paper-plane"></i> Submit Feedback';
                });
            });
        }
    }
});
