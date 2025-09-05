<template>
  <CommonPage>
    <CrudTable
      ref="$table"
      :columns="columns"
      :get-data="getPipelines"
      :show-pagination="true"
    />
  </CommonPage>
</template>

<script setup>
import { ref, onMounted, h } from 'vue'
import { NTag, NButton } from 'naive-ui'
import { formatDate } from '@/utils'

import CommonPage from '@/components/page/CommonPage.vue'
import CrudTable from '@/components/table/CrudTable.vue'

import api from '@/api'

defineOptions({ name: 'GitLabPipelines' })

const props = defineProps({
  projectId: {
    type: [String, Number],
    required: true
  }
})

const $table = ref(null)

const columns = [
  {
    title: '流水线ID',
    key: 'id',
    width: 120,
    align: 'center'
  },
  {
    title: '状态',
    key: 'status',
    width: 120,
    align: 'center',
    render: (row) => {
      const statusMap = {
        success: { type: 'success', text: '成功' },
        failed: { type: 'error', text: '失败' },
        running: { type: 'info', text: '运行中' },
        pending: { type: 'warning', text: '等待中' },
        canceled: { type: 'default', text: '已取消' }
      }
      
      const status = statusMap[row.status] || { type: 'default', text: row.status }
      
      return h(
        NTag,
        {
          type: status.type,
          size: 'small'
        },
        { default: () => status.text }
      )
    }
  },
  {
    title: '分支/标签',
    key: 'ref',
    width: 150,
    align: 'center'
  },
  {
    title: '提交SHA',
    key: 'sha',
    width: 120,
    align: 'center',
    ellipsis: { tooltip: true }
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 200,
    align: 'center',
    render: (row) => formatDate(row.created_at)
  },
  {
    title: '更新时间',
    key: 'updated_at',
    width: 200,
    align: 'center',
    render: (row) => formatDate(row.updated_at)
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

const getPipelines = async (params) => {
  try {
    const res = await api.getGitLabProjectPipelines(props.projectId, params)
    return {
      data: res.data,
      total: res.total
    }
  } catch (error) {
    console.error('Failed to fetch pipelines:', error)
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