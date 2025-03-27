const fetch = require('node-fetch');
const fs = require('fs');

async function fetchWithRetry(url, retries = 3, delay = 2000) {
    for (let i = 0; i < retries; i++) {
        try {
            const response = await fetch(url, { timeout: 10000 }); // 10초 타임아웃
            console.log('응답 상태:', response.status);
            if (!response.ok) throw new Error(`HTTP 오류: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error(`시도 ${i + 1}/${retries} 실패:`, error.message);
            if (i < retries - 1) await new Promise(resolve => setTimeout(resolve, delay));
            else throw error;
        }
    }
}

async function updateNews() {
    const SHEET_ID = process.env.SHEET_ID || '***';
    const API_KEY = process.env.API_KEY || '***';
    const NEWS_RANGE = '정세재난!C8:F';

    console.log('SHEET_ID:', SHEET_ID);
    console.log('API_KEY:', API_KEY);

    if (!SHEET_ID || !API_KEY) throw new Error('환경 변수가 설정되지 않음');

    try {
        const url = `https://sheets.googleapis.com/v4/spreadsheets/${SHEET_ID}/values/${NEWS_RANGE}?key=${API_KEY}`;
        console.log('요청 URL:', url);

        const data = await fetchWithRetry(url);
        console.log('응답 내용:', JSON.stringify(data));

        const today = new Date().toISOString().split('T')[0];
        const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];

        const newsItems = data.values
            .filter(row => {
                const dateStr = row[1];
                if (!dateStr) return false;
                const datePart = dateStr.split(' ')[0];
                return datePart === today || datePart === yesterday;
            })
            .map(row => ({
                title: row[0]?.trim() || '제목 없음',
                url: row[2]?.trim() || '#'
            }))
            .filter(item => item.title && item.title !== '제목 없음');

        fs.writeFileSync(
            'news.json',
            JSON.stringify(newsItems.length > 0 ? newsItems : [{ title: '최신 이틀치 데이터가 없습니다.', url: '#' }], null, 2)
        );
        console.log('news.json 업데이트 성공');
    } catch (error) {
        console.error('업데이트 실패:', error);
        fs.writeFileSync(
            'news.json',
            JSON.stringify([{ title: '데이터 업데이트 중 오류 발생', url: '#' }], null, 2)
        );
    }
}

updateNews();
