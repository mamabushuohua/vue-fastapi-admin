<template>
  <CommonPage back>
    <div class="project-details">
      <n-card v-if="project" title="项目信息">
        <n-descriptions label-placement="left" :column="1">
          <n-descriptions-item label="项目ID">
            {{ project.id }}
          </n-descriptions-item>
          <n-descriptions-item label="项目名称">
            {{ project.name }}
          </n-descriptions-item>
          <n-descriptions-item label="项目路径">
            {{ project.path }}
          </n-descriptions-item>
          <n-descriptions-item label="项目描述">
            {{ project.description || '-' }}
          </n-descriptions-item>
          <n-descriptions-item label="默认分支">
            {{ project.default_branch || '-' }}
          </n-descriptions-item>
          <n-descriptions-item label="项目地址">
            <n-button text type="primary" @click="openUrl(project.web_url)">
              {{ project.web_url }}
            </n-button>
          </n-descriptions-item>
          <n-descriptions-item label="SSH地址">
            {{ project.ssh_url }}
          </n-descriptions-item>
          <n-descriptions-item label="HTTP地址">
            {{ project.http_url }}
          </n-descriptions-item>
          <n-descriptions-item label="创建时间">
            {{ formatDate(project.created_at) }}
          </n-descriptions-item>
          <n-descriptions-item label="最后活动时间">
            {{ formatDate(project.last_activity_at) }}
          </n-descriptions-item>
        </n-descriptions>
      </n-card>

      <n-card v-if="project" title="项目标签" style="margin-top: 20px">
        <n-data-table
          :columns="tagColumns"
          :data="tags"
          :loading="tagsLoading"
          :pagination="tagPagination"
          remote
          @update:page="handleTagPageChange"
        />
      </n-card>

      <n-card v-if="project" title="最近提交" style="margin-top: 20px">
        <n-data-table
          :columns="commitColumns"
          :data="commits"
          :loading="commitsLoading"
          :pagination="commitPagination"
          remote
          @update:page="handleCommitPageChange"
        />
      </n-card>

      <n-card v-if="project" title="流水线" style="margin-top: 20px">
        <n-data-table
          :columns="pipelineColumns"
          :data="pipelines"
          :loading="pipelinesLoading"
          :pagination="pipelinePagination"
          remote
          @update:page="handlePipelinePageChange"
        />
      </n-card>
    </div>
  </CommonPage>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NCard, NDescriptions, NDescriptionsItem, NDataTable, NButton } from 'naive-ui'
import { formatDate } from '@/utils'

import CommonPage from '@/components/page/CommonPage.vue'
import api from '@/api'

defineOptions({ name: 'GitLabProjectDetails' })

const route = useRoute()
const router = useRouter()
const projectId = route.params.id

const project = ref(null)
const tags = ref([])
const commits = ref([])
const pipelines = ref([])

const tagsLoading = ref(false)
const commitsLoading = ref(false)
const pipelinesLoading = ref(false)

// 分页配置
const tagPagination = ref({
  page: 1,
  pageSize: 10,
  showSizePicker: true,
  pageSizes: [10, 20, 50],
  itemCount: 0,
  prefix({ itemCount }) {
    return `总计 ${itemCount} 条`
  }
})

const commitPagination = ref({
  page: 1,
  pageSize: 10,
  showSizePicker: true,
  pageSizes: [10, 20, 50],
  itemCount: 0,
  prefix({ itemCount }) {
    return `总计 ${itemCount} 条`
  }
})

const pipelinePagination = ref({
  page: 1,
  pageSize: 10,
  showSizePicker: true,
  pageSizes: [10, 20, 50],
  itemCount: 0,
  prefix({ itemCount }) {
    return `总计 ${itemCount} 条`
  }
})

// 标签表格列
const tagColumns = [
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

// 提交表格列
const commitColumns = [
  {
    title: '提交ID',
    key: 'short_id',
    width: 120,
    align: 'center'
  },
  {
    title: '提交标题',
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

// 流水线表格列
const pipelineColumns = [
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
        pending: { type: 'warning', text: '等待中' }
      }
      const status = statusMap[row.status] || { type: 'default', text: row.status }
      return h(
        NButton,
        {
          size: 'small',
          type: status.type
        },
        { default: () => status.text }
      )
    }
  },
  {
    title: '分支',
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

// 获取项目详情
const fetchProjectDetails = async () => {
  try {
    const res = await api.getGitLabProjectDetails(projectId)
    project.value = res.data
  } catch (error) {
    console.error('获取项目详情失败:', error)
  }
}

// 获取标签列表
const fetchTags = async (page = 1) => {
  tagsLoading.value = true
  try {
    const res = await api.getGitLabProjectTags(projectId, {
      page: page,
      pageSize: tagPagination.value.pageSize
    })
    tags.value = res.data
    tagPagination.value.itemCount = res.total
    tagPagination.value.page = page
  } catch (error) {
    console.error('获取标签列表失败:', error)
  } finally {
    tagsLoading.value = false
  }
}

// 获取提交列表
const fetchCommits = async (page = 1) => {
  commitsLoading.value = true
  try {
    const res = await api.getGitLabProjectCommits(projectId, {
      page: page,
      pageSize: commitPagination.value.pageSize
    })
    commits.value = res.data
    commitPagination.value.itemCount = res.total
    commitPagination.value.page = page
  } catch (error) {
    console.error('获取提交列表失败:', error)
  } finally {
    commitsLoading.value = false
  }
}

// 获取流水线列表
const fetchPipelines = async (page = 1) => {
  pipelinesLoading.value = true
  try {
    const res = await api.getGitLabProjectPipelines(projectId, {
      page: page,
      pageSize: pipelinePagination.value.pageSize
    })
    pipelines.value = res.data
    pipelinePagination.value.itemCount = res.total
    pipelinePagination.value.page = page
  } catch (error) {
    console.error('获取流水线列表失败:', error)
  } finally {
    pipelinesLoading.value = false
  }
}

// 处理标签分页变化
const handleTagPageChange = (page) => {
  fetchTags(page)
}

// 处理提交分页变化
const handleCommitPageChange = (page) => {
  fetchCommits(page)
}

// 处理流水线分页变化
const handlePipelinePageChange = (page) => {
  fetchPipelines(page)
}

// 打开链接
const openUrl = (url) => {
  window.open(url, '_blank')
}

onMounted(() => {
  fetchProjectDetails()
  fetchTags()
  fetchCommits()
  fetchPipelines()
})
</script>

<style scoped>
.project-details {
  max-width: 1200px;
  margin: 0 auto;
}
</style>