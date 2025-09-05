<template>
  <CommonPage>
    <CrudTable
      ref="$table"
      v-model:query-items="queryItems"
      :columns="columns"
      :get-data="api.getGitLabProjects"
      :show-pagination="true"
    >
      <template #queryBar>
        <QueryBarItem label="项目名称" :label-width="70">
          <NInput
            v-model:value="queryItems.name"
            clearable
            type="text"
            placeholder="请输入项目名称"
            @keypress.enter="$table?.handleSearch()"
          />
        </QueryBarItem>
      </template>
    </CrudTable>
  </CommonPage>
</template>

<script setup>
import { ref, h } from 'vue'
import { useRouter } from 'vue-router'
import { NInput, NButton, NTag } from 'naive-ui'
import { formatDate } from '@/utils'

import CommonPage from '@/components/page/CommonPage.vue'
import QueryBarItem from '@/components/query-bar/QueryBarItem.vue'
import CrudTable from '@/components/table/CrudTable.vue'

import api from '@/api'

defineOptions({ name: 'GitLabProjects' })

const router = useRouter()
const $table = ref(null)
const queryItems = ref({})

const columns = [
  {
    title: '项目ID',
    key: 'id',
    width: 100,
    align: 'center'
  },
  {
    title: '项目名称',
    key: 'name',
    width: 200,
    align: 'center',
    ellipsis: { tooltip: true }
  },
  {
    title: '项目路径',
    key: 'path',
    width: 200,
    align: 'center',
    ellipsis: { tooltip: true }
  },
  {
    title: '项目描述',
    key: 'description',
    align: 'center',
    ellipsis: { tooltip: true }
  },
  {
    title: '项目地址',
    key: 'web_url',
    align: 'center',
    ellipsis: { tooltip: true },
    render: (row) => {
      return h(
        NButton,
        {
          text: true,
          type: 'primary',
          onClick: () => window.open(row.web_url, '_blank')
        },
        { default: () => '访问' }
      )
    }
  },
  {
    title: '最后活动时间',
    key: 'last_activity_at',
    width: 200,
    align: 'center',
    render: (row) => formatDate(row.last_activity_at)
  },
  {
    title: '操作',
    key: 'actions',
    width: 200,
    align: 'center',
    fixed: 'right',
    render: (row) => {
      return [
        h(
          NButton,
          {
            size: 'small',
            type: 'primary',
            secondary: true,
            onClick: () => {
              // Navigate to project details
              console.log('Navigate to project details', row.id)
              router.push(`/gitlab/projects/${row.id}`)
            }
          },
          { default: () => '详情' }
        )
      ]
    }
  }
]
</script>