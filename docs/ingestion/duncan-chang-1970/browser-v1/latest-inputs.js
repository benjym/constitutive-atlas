async (page) => {
  const target=page.getByRole('spinbutton',{name:'Axial strain (%)',exact:true});
  await target.fill('0.2');
  await target.fill('0.3');
  await target.fill('0.4');
  await page.getByText('✓ Response up to date',{exact:true}).waitFor();
  return {target:await target.inputValue(),history_kPa:await page.getByRole('spinbutton',{name:'h (kPa)',exact:true}).inputValue(),K:await page.getByRole('spinbutton',{name:'Primary modulus number',exact:true}).inputValue(),detail:await page.locator('#run-detail').textContent()};
}
