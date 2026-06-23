<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  option: { type: Object, required: true },
  ariaLabel: { type: String, required: true },
})

const chartElement = ref()
let chart
let resizeObserver

function renderChart() {
  if (!chart) return
  chart.setOption(props.option, { notMerge: true, lazyUpdate: true })
}

onMounted(() => {
  chart = echarts.init(chartElement.value)
  renderChart()
  resizeObserver = new ResizeObserver(() => chart?.resize())
  resizeObserver.observe(chartElement.value)
})

watch(() => props.option, renderChart, { deep: true })

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  chart?.dispose()
})
</script>

<template>
  <div ref="chartElement" class="responsive-echart" role="img" :aria-label="ariaLabel"></div>
</template>

<style scoped>
.responsive-echart { width: 100%; height: 286px; }
</style>
