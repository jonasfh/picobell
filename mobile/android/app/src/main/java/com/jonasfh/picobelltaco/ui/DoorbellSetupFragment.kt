package com.jonasfh.picobelltaco.ui

import android.os.Bundle
import android.util.Log
import android.view.*
import android.widget.LinearLayout
import android.widget.TextView
import androidx.fragment.app.Fragment
import com.jonasfh.picobelltaco.R

class DoorbellSetupFragment : Fragment(), HasMenu {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setHasOptionsMenu(true)
        MainMenu.setup(this)
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val layout = LinearLayout(requireContext()).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(50, 50, 50, 50)
        }

        val txt = TextView(requireContext()).apply {
            text = "Dørklokke-oppsett\n(Koble til Pico via BLE)"
            textSize = 22f
        }

        layout.addView(txt)
        return layout
    }

    override fun onCreateOptionsMenu(menu: Menu, inflater: MenuInflater) {
        MainMenu.inflate(menu, inflater)
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        return when (item.itemId) {
            R.id.menu_profile -> {
                parentFragmentManager.beginTransaction()
                    .replace(
                        (view?.parent as ViewGroup).id,
                        ProfileFragment()
                    )
                    .addToBackStack(null)
                    .commit()
                true
            }
            else -> super.onOptionsItemSelected(item)
        }
    }

    override fun onMenuSelected(item: MenuItem): Boolean = false
}
