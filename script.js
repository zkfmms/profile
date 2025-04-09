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
    document.getElementById('ask-button').addEventListener('click', async function() {
        const question = document.getElementById('user-question').value.trim();
        if (!question) return;
        
        // Loading状態の表示
        const answerContainer = document.getElementById('answer-container');
        const answerText = document.getElementById('answer-text');
        answerContainer.classList.remove('hidden');
        answerText.innerHTML = '<div class="loader"></div>';
        
        try {
            // Google Apps Scriptを呼び出してAI応答を取得
            const scriptUrl = 'https://script.google.com/macros/s/AKfycbxlvt3GmjSkuNPlZxdMrWQxfOoJop0FUAWQbdXrpSdt8uDTFOyRCl7ZH3nRhy7-0tTn/exec';
            
            const response = await fetch(scriptUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question: question })
            });
            
            if (response.ok) {
                const data = await response.json();
                answerText.textContent = data.response;
            } else {
                throw new Error('応答の取得に失敗しました');
            }
        } catch (error) {
            console.error('Error:', error);
            answerText.textContent = "申し訳ありません。ただいま応答システムがメンテナンス中です。直接メールでお問い合わせいただくか、後ほど再度お試しください。";
        }
    });
});