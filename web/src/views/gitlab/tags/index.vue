<template>
  <CommonPage>
    <CrudTable
      ref="$table"
      :columns="columns"
      :get-data="getTags"
      :show-pagination="true"
    />
  </CommonPage>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { NTag } from 'naive-ui'
import { formatDate } from '@/utils'

import CommonPage from '@/components/page/CommonPage.vue'
import CrudTable from '@/components/table/CrudTable.vue'

import api from '@/api'

defineOptions({ name: 'GitLabTags' })

const props = defineProps({
  projectId: {
    type: [String, Number],
    required: true
  }
})

const $table = ref(null)

const columns = [
  {
    title: '标签名称',
    key: 'name',
    width: 200,
    align: 'center'
  },
  {
    title: '提交ID',
    key: 'commit.id',
    width: 150,
    align: 'center',
    render: (row) => row.commit ? row.commit.short_id : '-'
  },
  {
    title: '提交时间',
    key: 'commit.created_at',
    width: 200,
    align: 'center',
    render: (row) => row.commit ? formatDate(row.commit.created_at) : '-'
  },
  {
    title: '标签信息',
    key: 'message',
    align: 'center',
    ellipsis: { tooltip: true }
  }
]

const getTags = async (params) => {
  try {
    const res = await api.getGitLabProjectTags(props.projectId)
    return {
      data: res.data,
      total: res.total
    }
  } catch (error) {
    console.error('Failed to fetch tags:', error)
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