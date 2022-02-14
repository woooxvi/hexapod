package com.rookiedev.hexapod.view

import android.content.Context
import android.util.AttributeSet
import android.view.ViewGroup

class ControlView : ViewGroup {
    private val mContext: Context? = null

    constructor(context: Context) : super(context) {
        // ...
    }

    constructor(context: Context, attrs: AttributeSet?) : super(context, attrs) {
        // ...
    }

    override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
        TODO("Not yet implemented")
    }

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        super.onMeasure(widthMeasureSpec, heightMeasureSpec)
    }

}
