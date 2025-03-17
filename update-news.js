const fetch = require('node-fetch');
const fs = require('fs');

async function updateNews() {
    const response = await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${SHEET_ID}/values/${RANGE}?key=${API_KEY}`);
    const data = await response.json();
    const today = new Date().toISOString().split('T')[0];
    const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];
    const newsItems = data.values
        .filter(row => {
            const dateStr = row[1];
            if (!dateStr) return false;
            const datePart = dateStr.split(' ')[0];
            return datePart === today || datePart === yesterday;
        })
        .map(row => ({ title: row[0], url: row[2] || '#' }))
        .filter(item => item.title && item.title.trim() !== '');
    if (newsItems.length === 0) {
        newsItems.push({ title: '최신 이틀치 데이터가 없습니다.', url: '#' });
    }
    fs.writeFileSync('news.json', JSON.stringify(newsItems));
}

updateNews();
