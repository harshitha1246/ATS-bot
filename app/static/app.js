const files = document.querySelector('#files');
const fileList = document.querySelector('#file-list');
const analyze = document.querySelector('#analyze');
const conversation = document.querySelector('#conversation');
const results = document.querySelector('#results');

files.addEventListener('change', () => {
  fileList.textContent = files.files.length ? [...files.files].map(file => file.name).join('  /  ') : 'No files selected yet.';
});
analyze.addEventListener('click', async () => {
  if (!files.files.length) return addMessage('Please choose a JD and at least one resume first.', 'error');
  const body = new FormData();
  [...files.files].forEach(file => body.append('files', file));
  analyze.disabled = true; analyze.textContent = 'Analyzing...';
  try {
    const response = await fetch('/api/analyze', { method:'POST', body });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Analysis failed');
    render(data);
    addMessage(`I identified ${data.identified_jd} as the job description and analyzed ${data.analyses.length} resume(s).`, 'bot');
  } catch (error) { addMessage(error.message, 'error'); }
  finally { analyze.disabled = false; analyze.innerHTML = 'Analyze files <span>↗</span>'; }
});
function addMessage(text, kind) { const message = document.createElement('div'); message.className = `message ${kind}`; message.textContent = text; conversation.append(message); }
function list(items) { return items.length ? `<ul>${items.map(item => `<li>${escapeHtml(item)}</li>`).join('')}</ul>` : '<p>None identified.</p>'; }
function courseList(items) { return items.length ? `<ol>${items.slice(0, 4).map(item => `<li><a href="${escapeAttribute(item.url)}" target="_blank" rel="noreferrer">${escapeHtml(item.title)}</a></li>`).join('')}</ol>` : '<p>No targeted course found.</p>'; }
function breakdown(items) { return `<ul>${Object.entries(items).map(([name, value]) => `<li>${escapeHtml(name.replaceAll('_', ' '))}: ${value} points</li>`).join('')}</ul>`; }
function render(data) {
  results.hidden = false;
  results.innerHTML = `<div class="result-head"><h2>Analysis results</h2><span class="mono">JD: ${escapeHtml(data.identified_jd)}</span></div>
  <div class="ranking">${data.ranking.map(item => `<div class="rank"><strong>#${item.rank}</strong><span>${escapeHtml(item.resume)}</span><strong>${item.score}</strong><span class="mono">${item.alignment}</span></div>`).join('')}</div>
  ${data.analyses.map(item => `<article class="analysis"><h3>${escapeHtml(item.resume_name)}</h3><div class="score">${item.score}<small>/100</small></div><p><strong>JD alignment:</strong> ${item.alignment_rating} - ${item.alignment_percentage}%</p><div class="grid"><div class="block"><h4>Matched skills</h4>${list(item.matched_skills)}</div><div class="block"><h4>Missing skills</h4>${list(item.missing_skills)}</div><div class="block"><h4>Important gaps and why</h4>${list(item.gap_explanations)}</div><div class="block"><h4>Course recommendations</h4>${courseList(item.course_links)}</div><div class="block"><h4>Score breakdown</h4>${breakdown(item.score_breakdown)}</div></div><p>${escapeHtml(item.explanation)}</p></article>`).join('')}`;
}
function escapeHtml(value) { return String(value).replace(/[&<>'"]/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;', '"':'&quot;'}[char])); }
function escapeAttribute(value) { return escapeHtml(value).replace(/javascript:/gi, ''); }
