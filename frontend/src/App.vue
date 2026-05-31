<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

const API = 'http://localhost:8000'

const documents = ref<string[]>([])
const uploadStatus = ref('')
const fileInput = ref<HTMLInputElement | null>(null)

const question = ref('')
const selectedSource = ref('')
const answer = ref('')
const sources = ref<any[]>([])
const loading = ref(false)

async function loadDocuments() {
  try {
    const res = await axios.get(`${API}/documents`)
    documents.value = res.data.documents
  } catch {
    documents.value = []
  }
}

async function uploadFile() {
  const file = fileInput.value?.files?.[0]
  if (!file) return
  const formData = new FormData()
  formData.append('file', file)
  uploadStatus.value = '上傳中...'
  try {
    const res = await axios.post(`${API}/ingest`, formData)
    uploadStatus.value = res.data.message
    await loadDocuments()
  } catch {
    uploadStatus.value = '上傳失敗'
  }
}

async function deleteDocument(filename: string) {
  if (!confirm(`確定刪除 ${filename}？`)) return
  try {
    await axios.delete(`${API}/documents/${encodeURIComponent(filename)}`)
    if (selectedSource.value === filename) selectedSource.value = ''
    await loadDocuments()
  } catch {
    alert('刪除失敗')
  }
}

async function ask() {
  if (!question.value.trim()) return
  loading.value = true
  answer.value = ''
  sources.value = []
  try {
    const res = await axios.post(`${API}/query`, {
      question: question.value,
      source: selectedSource.value || null
    })
    answer.value = res.data.answer
    sources.value = res.data.sources || []
  } catch {
    answer.value = '查詢失敗'
  } finally {
    loading.value = false
  }
}

onMounted(loadDocuments)
</script>

<template>
  <div class="container">
    <h1>📚 RAG 文件問答系統</h1>

    <section class="card">
      <h2>📁 文件管理</h2>
      <div class="upload-row">
        <input ref="fileInput" type="file" accept=".pdf,.docx" />
        <button @click="uploadFile">上傳</button>
        <span v-if="uploadStatus" class="status">{{ uploadStatus }}</span>
      </div>
      <div v-if="documents.length === 0" class="empty">尚未上傳任何文件</div>
      <ul v-else class="doc-list">
        <li v-for="doc in documents" :key="doc">
          <span>📄 {{ doc }}</span>
          <button class="del-btn" @click="deleteDocument(doc)">刪除</button>
        </li>
      </ul>
    </section>

    <section class="card">
      <h2>💬 提問</h2>
      <div class="select-row">
        <label>查詢範圍：</label>
        <select v-model="selectedSource">
          <option value="">全部文件</option>
          <option v-for="doc in documents" :key="doc" :value="doc">{{ doc }}</option>
        </select>
      </div>
      <div class="input-row">
        <input v-model="question" placeholder="輸入問題..." @keyup.enter="ask" />
        <button @click="ask" :disabled="loading">{{ loading ? '查詢中...' : '送出' }}</button>
      </div>
      <div v-if="answer" class="answer">
        <strong>回答：</strong>
        <p>{{ answer }}</p>
      </div>
      <div v-if="sources.length > 0" class="sources">
        <strong>參考來源：</strong>
        <div v-for="(s, i) in sources" :key="i" class="source-item">
          <span class="source-file">📄 {{ s.source }}</span>
          <span class="source-score">相似度 {{ (s.score * 100).toFixed(1) }}%</span>
          <p class="source-text">{{ s.text }}...</p>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.container { max-width: 800px; margin: 40px auto; padding: 0 20px; font-family: sans-serif; }
h1 { font-size: 1.8rem; margin-bottom: 24px; }
.card { background: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; margin-bottom: 24px; }
h2 { font-size: 1.2rem; margin-bottom: 16px; }
.upload-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.status { color: #4a90e2; font-size: 0.9rem; }
.empty { color: #999; font-size: 0.9rem; margin-top: 8px; }
.doc-list { list-style: none; padding: 0; margin-top: 12px; }
.doc-list li { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #eee; }
.del-btn { background: #ff4d4f; color: white; border: none; padding: 4px 10px; border-radius: 4px; cursor: pointer; font-size: 0.85rem; }
.select-row { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
select { padding: 6px 10px; border: 1px solid #ccc; border-radius: 4px; }
.input-row { display: flex; gap: 8px; }
input[type="text"], input:not([type="file"]):not([type="button"]) { flex: 1; padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
button { padding: 8px 16px; background: #4a90e2; color: white; border: none; border-radius: 4px; cursor: pointer; }
button:disabled { background: #ccc; cursor: not-allowed; }
.answer { margin-top: 16px; background: white; padding: 12px; border-radius: 6px; border: 1px solid #e0e0e0; }
.sources { margin-top: 16px; }
.source-item { background: white; border: 1px solid #e0e0e0; border-radius: 6px; padding: 10px; margin-top: 8px; }
.source-file { font-weight: bold; font-size: 0.85rem; }
.source-score { float: right; color: #4a90e2; font-size: 0.85rem; }
.source-text { margin: 6px 0 0; font-size: 0.85rem; color: #555; }
</style>