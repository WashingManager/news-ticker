import fetch from 'node-fetch';
import fs from 'fs';

async function updateNews() {
    const SHEET_ID = process.env.SHEET_ID;
    const API_KEY = process.env.API_KEY;
    const NEWS_RANGE = '정세재난!C8:F';

    console.log('SHEET_ID:', SHEET_ID);
    console.log('API_KEY:', API_KEY);

    if (!SHEET_ID || !API_KEY) throw new Error('환경 변수가 설정되지 않음');

    try {
        const url = `https://sheets.googleapis.com/v4/spreadsheets/${SHEET_ID}/values/${NEWS_RANGE}?key=${API_KEY}`;
        console.log('요청 URL:', url);
        const response = await fetch(url);
        const text = await response.text();
        console.log('응답 상태:', response.status);
        console.log('응답 내용:', text);
        if (!response.ok) throw new Error(`HTTP 오류: ${response.status}`);

        const data = await JSON.parse(text);
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
