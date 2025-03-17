// statusButton.js
const STATUS_RANGE = '긴장혼잡도!A1:E4';

async function updateStatusFromSheet() {
    try {
        const response = await fetch(
            `https://sheets.googleapis.com/v4/spreadsheets/${window.SHEET_ID}/values/${STATUS_RANGE}?key=${window.API_KEY}`
        );
        if (!response.ok) throw new Error(`API 요청 실패: ${response.status}`);
        const data = await response.json();
        if (!data.values) throw new Error('데이터가 비어 있습니다.');

        const rows = data.values;
        const tensionRow = rows[1] || [];
        const tensionLevels = document.querySelectorAll('.status-bars .status-bar:nth-child(1) .status-levels .status-level');
        tensionLevels.forEach((level, index) => {
            level.classList.remove('active');
            if (tensionRow[index + 1] === '1') level.classList.add('active');
        });

        const congestionRow = rows[3] || [];
        const congestionLevels = document.querySelectorAll('.status-bars .status-bar:nth-child(2) .status-levels .status-level');
        congestionLevels.forEach((level, index) => {
            level.classList.remove('active');
            if (congestionRow[index + 1] === '1') level.classList.add('active');
        });
    } catch (error) {
        console.error('상태 데이터 로드 실패:', error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    updateStatusFromSheet();
    setInterval(updateStatusFromSheet, 60000);
});
