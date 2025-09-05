<template>
  <CommonPage>
    <div class="mb-3">
      <NInput
        v-model:value="queryItems.ref_name"
        clearable
        placeholder="请输入分支或标签名称"
        @keypress.enter="$table?.handleSearch()"
      >
        <template #prefix>
          <span class="text-xs">分支/标签:</span>
        </template>
      </NInput>
    </div>
    
    <CrudTable
      ref="$table"
      v-model:query-items="queryItems"
      :columns="columns"
      :get-data="getCommits"
      :show-pagination="true"
    />
  </CommonPage>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { NInput } from 'naive-ui'
import { formatDate } from '@/utils'

import CommonPage from '@/components/page/CommonPage.vue'
import CrudTable from '@/components/table/CrudTable.vue'

import api from '@/api'

defineOptions({ name: 'GitLabCommits' })

const props = defineProps({
  projectId: {
    type: [String, Number],
    required: true
  }
})

const $table = ref(null)
const queryItems = ref({
  ref_name: ''
})

const columns = [
  {
    title: '提交ID',
    key: 'short_id',
    width: 120,
    align: 'center'
  },
  {
    title: '标题',
    key: 'title',
    align: 'center',
    ellipsis: { tooltip: true }
  },
  {
    title: '作者',
    key: 'author_name',
    width: 150,
    align: 'center'
  },
  {
    title: '提交时间',
    key: 'created_at',
    width: 200,
    align: 'center',
    render: (row) => formatDate(row.created_at)
  },
  {
    title: '操作',
    key: 'actions',
    width: 100,
    align: 'center',
    render: (row) => {
      return h(
        NButton,
        {
          text: true,
          type: 'primary',
          onClick: () => window.open(row.web_url, '_blank')
        },
        { default: () => '查看' }
      )
    }
  }
]

const getCommits = async (params) => {
  try {
    const res = await api.getGitLabProjectCommits(props.projectId, params)
    return {
      data: res.data,
      total: res.total
    }
  } catch (error) {
    console.error('Failed to fetch commits:', error)
    return {
      data: [],
      total: 0
    }
  }
}

onMounted(() => {
  $table.value?.handleSearch()
})
</script>