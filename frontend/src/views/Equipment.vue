<template>
  <div>
    <el-card>
      <template #header>
        <div style="font-size: 16px; font-weight: bold">
          <span>实验设备管理</span>
        </div>
      </template>
      <!----------------------------------查询组件-------------------------------------------------->
      <div style="margin-bottom: 10px">
        <el-input
          placeholder="请输入设备名称查询"
          v-model="params.keywords"
          style="width: 240px; margin-right: 8px"
          clearable
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        ></el-input>
        <el-select
          placeholder="请选择实验室"
          v-model="params.lab_id"
          style="width: 200px; margin-right: 8px"
          clearable
          @change="handleSearch"
          @clear="handleSearch"
        >
          <el-option v-for="item in labOptions" :key="item.id" :value="item.id" :label="item.name">
          </el-option>
        </el-select>
        <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
        <template v-if="isAdmin">
          <el-button type="success" :icon="Plus" @click="handleCreate">新增</el-button>
        </template>
      </div>
      <!----------------------------------表格代码Table-------------------------------------------------->
      <el-table
        :header-cell-style="{ backgroundColor: '#f5f7fa', color: '#333', textAlign: 'center' }"
        :cell-style="{ textAlign: 'center' }"
        :data="tableData"
        style="width: 100%; text-align: center"
        v-loading="loading"
      >
        <el-table-column prop="lab_name" label="所属实验室" />
        <el-table-column prop="name" label="设备名称" />
        <el-table-column prop="img" label="图片" width="90">
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
        <el-table-column prop="spec" label="型号规格" />
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ row.status === 1 ? '正常' : '维修' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button type="primary" text bg @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" text bg @click="handleDel(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!----------------------------------------------- 分页 ------------------------------------------------->
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
    <!----------------------------------点击弹窗（表单代码）-------------------------------------------------->
    <el-dialog v-model="dialogTableVisible" :title="form.id ? '编辑' : '新增'" width="450">
      <el-form
        ref="formRef"
        :rules="rules"
        :model="form"
        label-width="100px"
        style="width: 100%; padding-right: 30px; padding-top: 16px"
        v-loading="loading"
      >
        <el-form-item label="所属实验室" prop="lab_id">
          <el-select v-model="form.lab_id" placeholder="请选择实验室" style="width: 100%">
            <el-option
              v-for="item in labOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="设备名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入设备名称" />
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入说明" />
        </el-form-item>
        <el-form-item label="图片">
          <el-upload
            :http-request="handleFileUpload"
            :show-file-list="false"
            accept="image/jpeg,image/png,image/gif,image/webp"
          >
            <img
              v-if="form.img"
              :src="form.img"
              style="width: 80px; height: 80px; border-radius: 6px; display: block"
            />
            <el-button v-else type="primary" plain>上传图片</el-button>
          </el-upload>
        </el-form-item>
        <el-form-item label="型号规格">
          <el-input v-model="form.spec" placeholder="例如 RTX4090 24G" />
        </el-form-item>
        <el-form-item label="数量" prop="quantity">
          <el-input-number v-model="form.quantity" controls-position="right" :min="1" :max="999" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio :value="1">正常</el-radio>
            <el-radio :value="0">维修</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogTableVisible = false">取消</el-button>
        <el-button type="primary" :loading="formLoading" @click="handleSave">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { Search, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import {
  createEquipmentApi,
  deleteEquipmentApi,
  getEquipmentPageListApi,
  updateEquipmentApi
} from '@/api/equipment'

import { getLabPageListApi } from '@/api/lab'
import { uploadFileApi } from '@/api/file'
import { useUser } from '@/utils/user'

const { userInfo } = useUser()
const isAdmin = computed(() => userInfo.value?.role === 'admin')

const tableData = ref([])
const labOptions = ref([])
const total = ref(0)
const dialogTableVisible = ref(false)
const formRef = ref()
const form = reactive({
  id: null,
  lab_id: null,
  name: '',
  description: '',
  img: '',
  spec: '',
  quantity: 1,
  status: 1
})
const loading = ref(false)
const formLoading = ref(false)

//重置表单
const resetForm = () => {
  Object.assign(form, {
    id: null,
    lab_id: null,
    name: '',
    description: '',
    img: '',
    spec: '',
    quantity: 1,
    status: 1
  })
}

const rules = {
  lab_id: [{ required: true, message: '请选择实验室', trigger: 'change' }],
  name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }]
}

const params = reactive({
  page: 1,
  pageSize: 8,
  keywords: '',
  lab_id: null
})

//获得实验设备列表
const load = async () => {
  loading.value = true
  try {
    const res = await getEquipmentPageListApi({
      page: params.page,
      page_size: params.pageSize,
      keywords: params.keywords,
      lab_id: params.lab_id
    })
    if (res.code === 200) {
      tableData.value = res.data?.list
      total.value = res.data?.total
    }
  } finally {
    loading.value = false
  }
}

const loadLabs = async () => {
  const res = await getLabPageListApi({
    page: 1,
    page_size: 100
  })
  if (res.code === 200) {
    labOptions.value = res.data?.list
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

//保存新增实验设备
const handleSave = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  formLoading.value = true
  try {
    const res = form.id ? await updateEquipmentApi(form.id, form) : await createEquipmentApi(form)
    if (res.code === 200) {
      dialogTableVisible.value = false
      ElMessage.success('操作成功')
      load()
    }
  } finally {
    formLoading.value = false
    dialogTableVisible.value = false
  }
}
//编辑实验设备
const handleEdit = (row) => {
  resetForm()
  Object.assign(form, {
    id: row.id,
    lab_id: row.lab_id,
    name: row.name,
    description: row.description,
    img: row.img,
    spec: row.spec,
    quantity: row.quantity,
    status: row.status
  })
  dialogTableVisible.value = true
}

//删除实验室
const handleDel = (row) => {
  ElMessageBox.confirm(`确认删除实验室设备: [${row.name}] 吗？`, '确认删除', {
    type: 'warning'
  }).then(async () => {
    const res = await deleteEquipmentApi(row.id)
    if (res.code === 200) {
      ElMessage.success('删除成功')
      load()
    }
  })
}

//钩子函数重载
onMounted(() => {
  load()
  loadLabs()
})
</script>
