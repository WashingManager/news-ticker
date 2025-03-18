const fetch = require('node-fetch');
const fs = require('fs');

async function updateStatus() {
    const SHEET_ID = process.env.SHEET_ID;
    const API_KEY = process.env.API_KEY;
    const STATUS_RANGE = '긴장혼잡도!A1:E4';

    try {
        const response = await fetch(
            `https://sheets.googleapis.com/v4/spreadsheets/${SHEET_ID}/values/${STATUS_RANGE}?key=${API_KEY}`
        );
        if (!response.ok) throw new Error(`API 요청 실패: ${response.status}`);
        const data = await response.json();
        if (!data.values) throw new Error('데이터 비어 있음');

        const rows = data.values;
        const tension = rows[1]?.slice(1).map(v => v === '1') || [false, false, false, false];
        const congestion = rows[3]?.slice(1).map(v => v === '1') || [false, false, false];

        fs.writeFileSync('status.json', JSON.stringify({ tension, congestion }, null, 2));
    } catch (error) {
        console.error('상태 업데이트 실패:', error);
        fs.writeFileSync('status.json', JSON.stringify({ tension: [], congestion: [] }, null, 2));
    }
}

updateStatus();
