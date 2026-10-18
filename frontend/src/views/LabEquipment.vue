<template>
  <div>
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <div style="font-size: 16px; font-weight: bold">
            <span>{{ lab?.name || '实验室' }}设备列表</span>
          </div>
          <div>
            <el-button @click="router.push('/manager/lablist')">返回</el-button>
            <el-button type="primary" @click="handlReserveLab">预约实验室</el-button>
          </div>
        </div>
      </template>
      <div
        v-if="lab"
        style="
          color: #666;
          margin-bottom: 16px;
          background-color: #f4f5ff;
          padding: 10px;
          border-radius: 6px;
        "
      >
        <div style="margin-bottom: 10px">简介：{{ lab.description }}</div>
        <div>
          位置：{{ lab.location }} <span style="margin: 0 10px">|</span> 容纳 {{ lab.capacity }} 人
          <span style="margin: 0 10px">|</span>
          开放：{{ lab.open_time && lab.close_time ? `${lab.open_time} - ${lab.close_time}` : '-' }}
        </div>
      </div>
      <!-------------------------------------------------------------表格处------------------------------------------------------->
      <el-table
        :header-cell-style="{ backgroundColor: '#f5f7fa', color: '#333', textAlign: 'center' }"
        :cell-style="{ textAlign: 'center' }"
        :data="tableData"
        style="width: 100%; text-align: center"
        v-loading="loading"
      >
        <el-table-column prop="name" label="设备名称" />
        <el-table-column prop="img" label="图片" width="100">
          <template #default="{ row }">
            <div style="min-height: 50px; display: flex; align-items: center">
              <img
                v-if="row.img"
                style="display: block; width: 80px; height: 80px; border-radius: 6px"
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
            <el-button
              :disabled="!row.status"
              type="primary"
              text
              bg
              @click="handleReserveEquipment(row)"
              >预约</el-button
            >
          </template>
        </el-table-column>
      </el-table>

      <!----------------------------------------------- 分页 ------------------------------------------------->
      <div style="margin-top: 10px; display: flex; justify-content: flex-end">
        <el-pagination
          v-model:current-page="params.page"
          v-model:page-size="params.page_size"
          :total="total"
          background
          layout="total, prev, pager, next"
          @current-change="loadEquipment"
        />
      </div>
    </el-card>
    <!-----------------------------------------预约弹窗组件↓ ------------------------------------------>
    <reserve-dialog
      v-model:visible="reserveVisible"
      :lab-id="lab?.id"
      :lab-name="lab?.name"
      :equipment-id="currentEquipment?.id"
      :equipment-name="currentEquipment?.name"
    >
    </reserve-dialog>
    <!-----------------------------------------预约弹窗组件 ↑------------------------------------------>
  </div>
</template>
<script setup>
import { getLabDetailsApi } from '@/api/lab'
import { ElMessage } from 'element-plus'
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import ReserveDialog from '@/components/ReserveDialog.vue'
import { getEquipmentPageListApi } from '@/api/equipment'

const lab = ref(null)

const route = useRoute()
const router = useRouter()
const tableData = ref([])
const total = ref(0)
const loading = ref(false)
const reserveVisible = ref(false)

const currentEquipment = ref(null)
const params = reactive({
  page: 1,
  page_size: 8,
  keywords: '',
  lab_id: Number(route.query.lab_id) // "8" -> 8
})

const loadLab = async () => {
  if (!params.lab_id) {
    ElMessage.error('缺少实验室查询条件 [lab_id]')
    return
  }
  const res = await getLabDetailsApi(params.lab_id)
  if (res.code === 200) {
    lab.value = res.data
    console.log(lab.value)
  }
}

//获得实验设备列表
const loadEquipment = async () => {
  loading.value = true
  try {
    const res = await getEquipmentPageListApi({
      page: params.page,
      page_size: params.page_size,
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

const handlReserveLab = () => {
  if (lab.value.status != 1) {
    ElMessage.error('实验室正在维修，暂不可预约')
    router.push(`/manager/lab-equipment?lab_id=${lab.value.id}`)
  } else {
    currentEquipment.value = null
    reserveVisible.value = true
  }
}

const handleReserveEquipment = (equipment) => {
  currentEquipment.value = equipment
  reserveVisible.value = true
}

onMounted(() => {
  loadLab()
  loadEquipment()
})
</script>
