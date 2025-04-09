// タイピングアニメーション
document.addEventListener('DOMContentLoaded', function() {
    const typed = new Typed('#typewriter', {
        strings: [
            'AIを活用した業務自動化',
            'チャットボット・LINE連携開発',
            'SNS API活用・データ分析',
            'デザイン・ブランディング',
            '画像・音声・動画の解析と生成',
            'Webスクレイピング・情報収集'
        ],
        typeSpeed: 50,
        backSpeed: 20,
        backDelay: 1500,
        startDelay: 500,
        loop: true
    });

    // 最終更新日
    document.getElementById('last-updated').textContent = new Date().toLocaleDateString('ja-JP');
    
    // スクロールアニメーション
    const fadeElements = document.querySelectorAll('.card, .timeline-item, .project-card, .vision-item, .skill-category');
    
    const fadeInOnScroll = function() {
        fadeElements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const elementBottom = element.getBoundingClientRect().bottom;
            const isVisible = (elementTop < window.innerHeight) && (elementBottom > 0);
            
            if (isVisible) {
                element.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }
        });
    };
    
    // 初期状態を設定
    fadeElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
    });
    
    // スクロールイベントをリッスン
    window.addEventListener('scroll', fadeInOnScroll);
    // ページ読み込み時にも実行
    fadeInOnScroll();
    
    // Ask Me ボタンのイベントリスナー
});