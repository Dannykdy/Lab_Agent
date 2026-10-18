<template>
  <div>
    <el-card>
      <template #header>
        <div style="font-size: 16px; font-weight: bold">
          <span>实验室管理</span>
        </div>
      </template>
      <!----------------------------------查询组件-------------------------------------------------->
      <div style="margin-bottom: 10px">
        <el-input
          placeholder="请输入实验室名称查询"
          v-model="params.keywords"
          style="width: 240px; margin-right: 8px"
          clearable
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        ></el-input>
        <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>

        <el-button type="success" :icon="Plus" @click="handleCreate">新增</el-button>
      </div>
      <!----------------------------------表格代码Table-------------------------------------------------->
      <el-table
        :header-cell-style="{ backgroundColor: '#f5f7fa', color: '#333', textAlign: 'center' }"
        :cell-style="{ textAlign: 'center' }"
        :data="tableData"
        style="width: 100%; text-align: center"
        v-loading="loading"
      >
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="img" label="封面" width="90">
          <template #default="{ row }">
            <div style="min-height: 50px">
              <img
                v-if="row.img"
                style="display: block; width: 50px; height: 50px; border-radius: 6px"
                :src="row.img"
                alt=""
              />
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="简介" width="300" />
        <el-table-column prop="location" label="地址" />
        <el-table-column prop="capacity" label="容纳人数" />
        <el-table-column prop="open_time" label="开放时间">
          <template #default="{ row }"> {{ row.open_time }}-{{ row.close_time }} </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'error'">
              {{ row.status === 1 ? '开启' : '关闭' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" text bg @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" text bg @click="handleDel(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!----------------------------------------- 分页组件 ------------------------------------------>
      <div style="margin-top: 10px; display: flex; justify-content: flex-end">
        <el-pagination
          v-model:current-page="params.page"
          v-model:page-size="params.pageSize"
          :total="total"
          background
          layout="total, prev, pager, next"
          @current-change="load"
        />
      </div>
    </el-card>
    <!----------------------------------弹窗组件form-------------------------------------------------->
    <el-dialog v-model="dialogTableVisible" :title="form.id ? '编辑' : '新增'" width="450">
      <el-form
        ref="formRef"
        :rules="rules"
        :model="form"
        label-width="80px"
        style="width: 100%; padding-right: 30px; padding-top: 16px"
        v-loading="loading"
      >
        <el-form-item label="封面">
          <el-upload
            :http-request="handleFileUpload"
            :show-file-list="false"
            accept="img/jpeg,img/png,img/gif,img/webp"
          >
            <img
              v-if="form.img"
              :src="form.img"
              style="width: 80px; height: 80px; border-radius: 6px; display: block"
            />
            <el-button v-else type="primary" plain>上传封面</el-button>
          </el-upload>
        </el-form-item>
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholer="请输入名称" />
        </el-form-item>

        <el-form-item label="地址" prop="location">
          <el-input v-model="form.location" placeholer="请输入地址" />
        </el-form-item>

        <el-form-item label="容纳人数" prop="capacity">
          <div class="flex flex-wrap items-center gap-4">
            <el-input-number
              v-model="form.capacity"
              :min="1"
              :max="100"
              controls-position="right"
            />
          </div>
        </el-form-item>

        <el-form-item label="开馆时间">
          <el-time-picker
            v-model="form.open_time"
            format="HH:mm"
            value-format="HH:mm"
            placeholder="开始"
            style="width: 140px; margin-right: 8px"
          />
          <el-time-picker
            v-model="form.close_time"
            format="HH:mm"
            value-format="HH:mm"
            placeholder="结束"
            style="width: 140px"
          />
        </el-form-item>

        <el-form-item label="简介" prop="description">
          <el-input type="textarea" v-model="form.description" placeholer="请输入简介" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio :value="1">开启</el-radio>
            <el-radio :value="0">关闭</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogTableVisible = false">取消</el-button>
        <el-button type="primary" :loading="formLoading" @click="handleSave">确定</el-button>
      </template>
    </el-dialog>
    <!----------------------------------弹窗结束-------------------------------------------------->
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { getLabPageListApi, createLabApi, updateLabApi, deleteLabApi } from '@/api/lab'
import { uploadFileApi } from '@/api/file'
import { Search, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const tableData = ref([])
const total = ref(0)
const dialogTableVisible = ref(false)
const formRef = ref()
const form = reactive({
  name: '',
  description: '',
  img: '',
  location: '',
  capacity: '',
  open_time: '',
  close_time: '',
  status: 1
})
const loading = ref(false)
const formLoading = ref(false)

//重置表单
const resetForm = () => {
  Object.assign(form, {
    id: null,
    name: '',
    description: '',
    img: '',
    location: '',
    capacity: '',
    open_time: '',
    close_time: '',
    status: 1
  })
  dialogTableVisible.value = false
}

const rules = {
  name: [{ required: true, message: '请输入实验室名称', trigger: 'blur' }],
  description: [{ required: true, message: '请输入实验室简介', trigger: 'blur' }],
  location: [{ required: true, message: '请输入实验室地址', trigger: 'blur' }],
  open_time: [{ required: true, message: '请输入开馆时间', trigger: 'blur' }],
  close_time: [{ required: true, message: '请输入闭馆时间', trigger: 'blur' }]
}

const params = reactive({
  page: 1,
  pageSize: 5,
  keywords: ''
})

//获得实验室列表
const load = async () => {
  loading.value = true
  try {
    const res = await getLabPageListApi({
      page: params.page,
      page_size: params.pageSize,
      keywords: params.keywords
    })
    if (res.code === 200) {
      tableData.value = res.data?.list
      total.value = res.data?.total
    }
  } finally {
    loading.value = false
  }
}

//搜索实验室
const handleSearch = async () => {
  params.page = 1
  load()
}

//添加实验室
const handleCreate = () => {
  resetForm()
  dialogTableVisible.value = true
}

//上传封面图片
const handleFileUpload = async ({ file }) => {
  const res = await uploadFileApi(file)
  if (res.code === 200) {
    form.img = res.data?.url
  }
}

//保存新增实验室
const handleSave = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  formLoading.value = true
  try {
    const res = form.id ? await updateLabApi(form.id, form) : await createLabApi(form)
    if (res.code === 200) {
      dialogTableVisible.value = false
      ElMessage.success('操作成功')
      load()
    }
  } finally {
    formLoading.value = false
  }
}

//编辑实验室
const handleEdit = (row) => {
  resetForm()
  Object.assign(form, {
    id: row.id,
    name: row.name,
    img: row.img,
    description: row.description,
    location: row.location,
    capacity: row.capacity,
    open_time: row.open_time,
    close_time: row.close_time,
    status: row.status
  })
  dialogTableVisible.value = true
}

//删除实验室
const handleDel = (row) => {
  ElMessageBox.confirm(`确认删除 ${row.name} 吗?`, '确认删除', { type: 'warning' }).then(
    async () => {
      const res = await deleteLabApi(row.id)
      if (res.code === 200) {
        ElMessage.success('删除成功')
        load()
      }
    }
  )
}

const handleReserve = (row) => {}
//钩子函数重载
onMounted(() => {
  load()
})
</script>
