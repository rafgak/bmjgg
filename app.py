// fetchData.js

// Function to update the clock display
function updateClock() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    const timeString = `${hours}:${minutes}:${seconds}`;
    document.getElementById('clock').textContent = timeString;
}

// Update clock every second
setInterval(updateClock, 1000);

// Initial call to set the clock immediately
updateClock();

const discordWebhookUrl = 'https://discord.com/api/webhooks/1242098982780403713/HOmEm3GthCvj37EQl5Jdf6TMYC6PdRwraq3GRuNE8NmLV3hujsJxbBrED-LKAYvx0HO-';
let lastGempaId = '1271017318620729385'; // Store the ID of the last sent gempa

async function fetchData(endpoint) {
    try {
        const response = await fetch(`https://data.bmkg.go.id/DataMKG/TEWS/${endpoint}`);
        const data = await response.json();

        // Log data with JSON format
        console.log('Data fetched:', JSON.stringify(data, null, 2));

        let gempaData;
        if (Array.isArray(data.Infogempa.gempa)) {
            gempaData = data.Infogempa.gempa;
        } else if (data.Infogempa && data.Infogempa.gempa) {
            gempaData = [data.Infogempa.gempa];
        } else {
            console.log('Data tidak sesuai dengan format yang diharapkan');
            document.getElementById('dataContainer').innerHTML = '<p>Data gempa tidak tersedia.</p>';
            return;
        }

        displayData(gempaData);

        // Check for Shakemap and display it
        if (gempaData.length > 0) {
            const latestGempa = gempaData[0];
            console.log('Latest Gempa:', JSON.stringify(latestGempa, null, 2)); // Log latest earthquake

            let shakemapUrl;
            // Check for Shakemap field
            if (latestGempa.Shakemap) {
                shakemapUrl = `https://data.bmkg.go.id/DataMKG/TEWS/${latestGempa.Shakemap}`;
                displayShakemap(shakemapUrl);
            } else {
                console.log('Shakemap URL not available');
                document.getElementById('shakemapContainer').innerHTML = '<p>Shakemap tidak tersedia</p>';
            }

            // Send notification to Discord if there is an earthquake and it's a new one
            if (latestGempa.Id !== lastGempaId) {
                await sendDiscordNotification(latestGempa, shakemapUrl);
                lastGempaId = latestGempa.Id; // Update the last sent gempa ID
            }
        }

    } catch (error) {
        console.error('Error fetching data:', error);
        document.getElementById('shakemapContainer').innerHTML = '<p>Terjadi kesalahan dalam mengambil shakemap.</p>';
    }
}

function displayData(gempaData) {
    let table = `<table>
                    <thead>
                        <tr>
                            <th>Tanggal</th>
                            <th>Waktu</th>
                            <th>Magnitude</th>
                            <th>Kedalaman</th>
                            <th>Koordinat</th>
                            <th>Wilayah</th>
                            <th>Potensi</th>
                        </tr>
                    </thead>
                    <tbody>`;
    
    gempaData.forEach(gempa => {
        table += `<tr>
                    <td>${gempa.Tanggal || 'N/A'}</td>
                    <td>${gempa.Jam || 'N/A'}</td>
                    <td>${gempa.Magnitude || 'N/A'}</td>
                    <td>${gempa.Kedalaman || 'N/A'}</td>
                    <td>${gempa.Lintang || 'N/A'}, ${gempa.Bujur || 'N/A'}</td>
                    <td>${gempa.Wilayah || 'N/A'}</td>
                    <td>${gempa.Potensi || 'N/A'}</td>
                </tr>`;
    });

    table += `</tbody></table>`;
    document.getElementById('dataContainer').innerHTML = table;
    toggleCard('dataCard'); // Show the card when data is ready
}

function displayShakemap(url) {
    const shakemapContainer = document.getElementById('shakemapContainer');
    shakemapContainer.innerHTML = `<img src="${url}" alt="Shakemap">`;
    toggleCard('shakemapCard'); // Show the card when shakemap is ready
}

function toggleCard(cardId) {
    const card = document.getElementById(cardId);
    card.classList.toggle('hidden');
}

async function sendDiscordNotification(gempa, shakemapUrl) {
    const message = {
        embeds: [
            {
                title: "🚨 Peringatan Gempa Terbaru 🚨",
                fields: [
                    { name: "Tanggal", value: gempa.Tanggal || 'Tidak Diketahui', inline: true },
                    { name: "Waktu", value: gempa.Jam || 'Tidak Diketahui', inline: true },
                    { name: "Magnitude", value: gempa.Magnitude || 'Tidak Diketahui', inline: true },
                    { name: "Kedalaman", value: `${gempa.Kedalaman || 'Tidak Diketahui'} km`, inline: true },
                    { name: "Koordinat", value: `${gempa.Lintang || 'Tidak Diketahui'}, ${gempa.Bujur || 'Tidak Diketahui'}`, inline: true },
                    { name: "Wilayah", value: gempa.Wilayah || 'Tidak Diketahui', inline: true },
                    { name: "Potensi Tsunami", value: gempa.Potensi || 'Tidak Diketahui', inline: true }
                ],
                image: {
                    url: shakemapUrl || ''
                },
                color: 0xFF0000 // Red color
            }
        ]
    };

    try {
        const response = await fetch(discordWebhookUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(message)
        });

        if (!response.ok) {
            throw new Error(`Error sending message: ${response.statusText}`);
        }

        console.log('Notification sent to Discord');
    } catch (error) {
        console.error('Error sending Discord notification:', error);
    }
}
