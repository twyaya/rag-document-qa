<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'

const question = ref('')
const answer = ref('')
const loading = ref(false)
const uploadStatus = ref('')
const fileInput = ref<HTMLInputElement | null>(null)

async function uploadFile() {
  const file = fileInput.value?.files?.[0]
  if (!file) return
  const formData = new FormData()
  formData.append('file', file)
  uploadStatus.value = '上傳中...'
  try {
    const res = await axios.post('http://localhost:8000/ingest', formData)
    uploadStatus.value = res.data.message
  } catch {
    uploadStatus.value = '上傳失敗'
  }
}

async function ask() {
  if (!question.value.trim()) return
  loading.value = true
  answer.value = ''
  try {
    const res = await axios.post('http://localhost:8000/query', {
      question: question.value
    })
    answer.value = res.data.answer
  } catch {
    answer.value = '查詢失敗'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="container">
    <h1>RAG 文件問答系統</h1>

    <section>
      <h2>上傳文件</h2>
      <input ref="fileInput" type="file" accept=".pdf,.docx" />
      <button @click="uploadFile">上傳</button>
      <p v-if="uploadStatus">{{ uploadStatus }}</p>
    </section>

    <section>
      <h2>提問</h2>
      <input v-model="question" placeholder="輸入問題..." @keyup.enter="ask" />
      <button @click="ask" :disabled="loading">
        {{ loading ? '查詢中...' : '送出' }}
      </button>
      <div v-if="answer" class="answer">
        <strong>回答：</strong>
        <p>{{ answer }}</p>
      </div>
    </section>
  </div>
</template>

<style scoped>
.container {
  max-width: 700px;
  margin: 40px auto;
  padding: 0 20px;
  font-family: sans-serif;
}
section {
  margin-bottom: 40px;
}
input[type="text"], input:not([type="file"]) {
  width: 100%;
  padding: 8px;
  margin: 8px 0;
  box-sizing: border-box;
}
button {
  padding: 8px 20px;
  margin-top: 8px;
  cursor: pointer;
}
.answer {
  margin-top: 16px;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 6px;
}
</style>