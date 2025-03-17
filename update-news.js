const fetch = require('node-fetch');
const fs = require('fs');

async function updateNews() {
    const SHEET_ID = process.env.SHEET_ID;
    const API_KEY = process.env.API_KEY;
    const RANGE = '정세재난!C8:F';

    try {
        const response = await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${SHEET_ID}/values/${RANGE}?key=${API_KEY}`);
        if (!response.ok) throw new Error(`HTTP 오류: ${response.status}`);
        const data = await response.json();

        if (!data.values || !Array.isArray(data.values)) {
            throw new Error('구글 시트 데이터 형식이 올바르지 않습니다.');
        }

        const today = new Date().toISOString().split('T')[0];
        const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];

        const newsItems = data.values
            .filter(row => {
                const dateStr = row[1];
                if (!dateStr || typeof dateStr !== 'string') return false;
                const datePart = dateStr.split(' ')[0];
                return datePart === today || datePart === yesterday;
            })
            .map(row => ({
                title: row[0]?.trim() || '제목 없음',
                url: row[2]?.trim() || '#'
            }))
            .filter(item => item.title && item.title !== '제목 없음');

        if (newsItems.length === 0) {
            newsItems.push({ title: '최신 이틀치 데이터가 없습니다.', url: '#' });
        }

        fs.writeFileSync('news.json', JSON.stringify(newsItems, null, 2)); // 포맷팅 추가로 가독성 향상
        console.log('news.json 업데이트 완료');
    } catch (error) {
        console.error('뉴스 업데이트 실패:', error);
        fs.writeFileSync('news.json', JSON.stringify([{ title: '데이터 업데이트 중 오류 발생', url: '#' }], null, 2));
    }
}

updateNews();
